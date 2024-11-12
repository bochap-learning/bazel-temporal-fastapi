import uvicorn
import sys

if __name__ =="__main__":
    sys.argv.insert(1, "service.api.server:app")
    sys.argv.append("--host")
    sys.argv.append("0.0.0.0")  # Listen on all interfaces    
    sys.exit(uvicorn.main())