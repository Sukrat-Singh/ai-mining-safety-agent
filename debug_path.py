import sys, os
print("PWD:", os.getcwd())
print("PATH entries containing 'mining':")
for p in sys.path:
    if "mining" in p.lower():
        print(" ->", p)

try:
    import src
    print("✅ src imported successfully")
except Exception as e:
    print("❌ ERROR importing src:", e)
