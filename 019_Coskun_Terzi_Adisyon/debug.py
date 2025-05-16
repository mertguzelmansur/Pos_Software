import traceback
import os
import sys

# Add the project root directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

try:
    from src import main
    main.main()
except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc()
    input("Press Enter to exit...") 