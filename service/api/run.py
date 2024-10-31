import uvicorn
import sys

if __name__ =="__main__":
    sys.argv.insert(1, "service.api.server:app")
    sys.exit(uvicorn.main())