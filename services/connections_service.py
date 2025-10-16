import requests

def check_llm_health(llm_url="http://localhost:8000/health"):
    try:
        resp = requests.get(llm_url, timeout=5)
        if resp.status_code == 200:
            return True,"Connected"
        else:
            return False,f"Unhealthy, status code {resp.status_code}"
    except Exception as e:
        return False,f"Failed: {e}"

def test_all_services(llm_url):
    status = {
        "LLM": check_llm_health(llm_url)
    }
    val_list = [check[0] for check in status.values()]
    return (True,status) if False not in val_list else (False, status)

# Example usage
# if __name__ == "__main__":
#     results = test_all_services(
#         qdrant_url="http://localhost:6333",
#         neo4j_uri="bolt://localhost:7687",
#         neo4j_user="neo4j",
#         neo4j_pass="password",
#         llm_url="http://localhost:1234/v1/models"
#     )
#     print(json.dumps(results,indent = 4))
