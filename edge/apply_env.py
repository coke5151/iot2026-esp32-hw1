Import("env")
import os
import re

env_file = os.path.abspath(os.path.join(env.get("PROJECT_DIR"), "..", ".env"))
if os.path.isfile(env_file):
    print(f"Loading .env from {env_file}")
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            
            # Remove inline comments
            v = re.split(r'\s+#', v)[0].strip()
            
            # Remove surrounding quotes if any
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
                
            # print(f"Adding CPPDEFINE: {k}")
            env.Append(CPPDEFINES=[(k, env.StringifyMacro(v))])
else:
    print(f"Warning: .env file not found at {env_file}")
