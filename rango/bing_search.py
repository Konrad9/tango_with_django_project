import json
import requests
import sys
import pprint

# Microsoft account key in bing.key
def read_bing_key():
    """ 
    reads the BING API key from a file called 'bing.key'
    returns a string which is either None, i.e. key not found, or with a key
    """
    bing_api_key = None
    try:
        with open("bing.key", "r") as f:
            bing_api_key = f.readline().strip()
    except:
        try:
            with open("../bing.key") as f:
                bing_api_key = f.readline().strip()
        except:
            raise IOError("bing.ket file not found")
            
    if not bing_api_key:
        raise KeyError("Bing key not found")
        
    return bing_api_key


def run_query(search_terms):
    bing_key = read_bing_key()
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": bing_key}
    params = {"q": search_terms, "textDecorations": True, "textFormat": "HTML"}
    
    # Issue the request, given the details above
    try:
        response = requests.get(search_url, headers = headers, params = params)
        response.raise_for_status()
        search_results = response.json()
    except:
        print("Connection error")
    
    # With the reponse in plat, build up a python list
    results = []
    for result in search_results["webPages"]["value"]:
        results.append({
                "title": result["name"],
                "link": result["url"],
                "summary": result["snippet"]})
    return results

def main():
    search_term = input("Search (type q to exit): ").strip()
    while search_term!="q":
        results = run_query(search_term)
        pprint.pprint(results)
        search_term = input("Search (type q to exit): ").strip()
    sys.exit()
    
    
if __name__ == "__main__":
    main()