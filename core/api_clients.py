import requests
import time
from typing import Dict, Any, List, Optional
from urllib.parse import quote

CLINGEN_BASE = "https://reg.clinicalgenome.org/allele"
MYVARIANT_BASE = "https://myvariant.info/v1/variant"
VEP_BASE = "https://rest.ensembl.org/vep/human/hgvs"
CLINVAR_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def retry_with_backoff(func, max_retries=3, initial_delay=1):
    """Retry a function with exponential backoff for rate limiting.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (doubles each retry)
        
    Returns:
        Function result or raises exception after max retries
    """
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
            raise
        except Exception as e:
            if attempt < max_retries - 1 and "429" in str(e):
                delay = initial_delay * (2 ** attempt)
                time.sleep(delay)
                continue
            raise
    raise Exception("Max retries exceeded")

def query_clingen(hgvs: str) -> Dict[str, Any]:
    """Query ClinGen Allele Registry API for variant information.
    
    Args:
        hgvs: HGVS notation (e.g., 'NM_000277.3:c.1521G>A')
        
    Returns:
        Dict with variant information or error message
    """
    try:
        # Ensure the HGVS is properly URL-encoded
        encoded_hgvs = quote(hgvs, safe=':.')
        url = f"{CLINGEN_BASE}/{encoded_hgvs}"
        
        # Add necessary headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Make the request
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        return resp.json()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"Variant {hgvs} not found in ClinGen Allele Registry"}
        return {"error": f"ClinGen API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error querying ClinGen: {str(e)}"}

def query_myvariant(identifier: str) -> Dict[str, Any]:
    """Query MyVariant.info API with retry logic for rate limiting."""
    def _query():
        resp = requests.get(f"{MYVARIANT_BASE}/{identifier}", params={"assembly": "hg38"}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    
    try:
        return retry_with_backoff(_query, max_retries=3, initial_delay=2)
    except Exception as e:
        return {"error": f"Error querying MyVariant: {str(e)}"}

def query_vep(hgvs: str) -> Dict[str, Any]:
    """Query Ensembl VEP API for variant effect prediction.

    Args:
        hgvs: HGVS notation (transcript, genomic, or rsID)

    Returns:
        Dict with VEP predictions or error message
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Check if this is an rsID (starts with 'rs')
    if hgvs.startswith('rs'):
        # For rsID, use the VEP /id endpoint directly
        url = f"https://rest.ensembl.org/vep/human/id/{quote(hgvs, safe='')}"
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        vep_response = resp.json()
        return vep_response

    # Check if this is protein-level HGVS (starts with 'NP_')
    if hgvs.startswith('NP_'):
        # VEP doesn't support protein-level HGVS
        return {"error": "VEP does not support protein-level HGVS notation (NP_...). Use transcript-level HGVS (NM_...) instead."}

    # For transcript/genomic HGVS notation, use the standard endpoint
    url = f"{VEP_BASE}/{quote(hgvs, safe='')}"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    vep_response = resp.json()
    return vep_response

def query_clinvar(variation_id: str = None, rsid: str = None, gene_symbol: Optional[str] = None) -> Dict[str, Any]:
    """Query ClinVar via NCBI E-utilities.
    
    Args:
        variation_id: ClinVar variation ID (e.g., '17662')
        rsid: dbSNP rsID (e.g., 'rs80357914' or '80357914')
    
    Returns:
        Dict with clinical significance, conditions, and review status
    """
    import xml.etree.ElementTree as ET
    
    # Clean rsID
    if rsid:
        rsid = rsid.replace('rs', '')
    
    # Step 1: Search for the variant
    search_url = f"{CLINVAR_BASE}/esearch.fcgi"
    if variation_id:
        search_term = f"{variation_id}[VariationID]"
    elif rsid:
        search_term = f"{rsid}[rs]"
    else:
        return {}
    
    search_params = {
        "db": "clinvar",
        "term": search_term,
        "retmode": "json"
    }
    
    try:
        search_resp = requests.get(search_url, params=search_params, timeout=15)
        search_resp.raise_for_status()
        search_data = search_resp.json()
        
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return {"error": "No ClinVar records found"}
        
        # Step 2: Fetch summary for the first ID
        summary_url = f"{CLINVAR_BASE}/esummary.fcgi"
        summary_params = {
            "db": "clinvar",
            "id": id_list[0],
            "retmode": "json"
        }
        
        summary_resp = requests.get(summary_url, params=summary_params, timeout=15)
        summary_resp.raise_for_status()
        summary_data = summary_resp.json()
        
        # Extract relevant fields
        result = summary_data.get("result", {})
        if id_list[0] in result:
            record = result[id_list[0]]
            
            # Extract germline classification (primary source of clinical significance)
            germline = record.get("germline_classification", {})
            clinical_sig = germline.get("description", "Not provided")
            review_status = germline.get("review_status", "Not provided")
            
            # Extract conditions from trait_set
            conditions = []
            for trait in germline.get("trait_set", []):
                trait_name = trait.get("trait_name")
                if trait_name:
                    conditions.append(trait_name)
            
            # Extract gene symbol
            gene_symbol = None
            if record.get("genes"):
                gene_symbol = record["genes"][0].get("symbol")
            
            return {
                "uid": record.get("uid"),
                "title": record.get("title"),
                "clinical_significance": clinical_sig,
                "review_status": review_status,
                "conditions": conditions,
                "gene_symbol": gene_symbol,
                "protein_change": record.get("protein_change"),
                "molecular_consequence": record.get("molecular_consequence_list", []),
            }
        
        return {"error": "Could not parse ClinVar response"}
        
    except Exception as e:
        return {"error": str(e)}
