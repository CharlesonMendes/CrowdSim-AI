import tinytroupe
import inspect
import pkgutil

print(f"TinyTroupe path: {tinytroupe.__path__}")

print("\nSubmodules:")
for importer, modname, ispkg in pkgutil.iter_modules(tinytroupe.__path__):
    print(f"- {modname}")

try:
    from tinytroupe.agent import TinyPerson
    print("\nSuccessfully imported TinyPerson")
except ImportError as e:
    print(f"\nFailed to import TinyPerson: {e}")

try:
    from tinytroupe.environment import TinyWorld
    print("Successfully imported TinyWorld")
except ImportError as e:
    print(f"Failed to import TinyWorld: {e}")
