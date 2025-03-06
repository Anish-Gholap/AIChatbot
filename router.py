from jigsawstack import JigsawStack
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException,BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

import os
import pandas as pd


load_dotenv()

# Initialise API app 
jigsawstack = JigsawStack()

# Router
router = APIRouter(
  prefix="/webscrape", #route prefix
  tags=["webscrape"],
  responses={404: {"description": "Not found"}}
)

# Validate request and response
class Request(BaseModel):
  url: HttpUrl
  element_prompts: List[str]
  format_type: Optional[str]= "json"  
class Response(BaseModel):
  success: bool
  message: str
  data: Optional[Dict[str, Any]] = None
  file_path: Optional[str] = None
  
# Save scrape results to csv
def save_to_csv(results: dict, file_path: str):

  if 'link' in results and isinstance(results['link'], list):
    df = pd.DataFrame(results['link'])
    df.to_csv(file_path, index=False)

# Format results for JSON Response
def format_results(results):
  formatted_data = {
        "metadata": {
            "url": results.get('link', 'No URL provided'),
            "success": results.get('success', False),
            "page_position": results.get('page_position', 'Unknown'),
            "page_position_length": results.get('page_position_length', 'Unknown')
        },
        "context": results.get('context', {}),
        "links": results.get('link', []),
        "data": []
    }
  
  if 'data' in results and isinstance(results['data'], list):
    for item in results['data']:
      data_item = {
        "key": item.get('key', 'Unknown'),
        "selector": item.get('selector', 'No selector'),
        "results": []
      }
      
      if 'results' in item and isinstance(item['results'], list):
          for result in item['results']:
              result_item = {
                  "text": result.get('text', 'No text'),
                  "html": result.get('html', 'No HTML'),
                  "attributes": result.get('attributes', [])
              }
              data_item["results"].append(result_item)
      
      formatted_data["data"].append(data_item)

  return formatted_data

# API ENDPOINTS

# Initiate webscrape of URL
@router.post("/scrape", response_model= Response)
async def scrape_url(request: Request, background_tasks: BackgroundTasks):
  
  try:
    # Initialise output directory if it doesnt exist
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(current_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Request Scrape
    params = {
      "url": str(request.url),
      "element_prompts": request.element_prompts
    }
    
    scrape_results = jigsawstack.web.ai_scrape(params)

    # Save results to csv
    if request.format_type == 'csv':
      file_path = os.path.join(results_dir, f"{request.element_prompts[0]}_results.csv")
      save_to_csv(scrape_results, file_path)
    
    # Format data for JSON response
    formatted_data = format_results(scrape_results)
    
    return Response(
      success=True,
      message=f"Successfully scraped {request.url}",
      data=formatted_data if request.format_type == "json" else None,
      file_path=file_path
    )
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
  


JIGSAWSTACK_API_KEY = sk_0a615682255fa53d65b95663952ef3315bd7e26e0d1ff08581307bc3b01d08f7aef5f79f2b0fa32c2c1620bf4b3b4cd6c669e95cd3194baf5bed80fb04117656024lAY3SELbnmuw75uBxX