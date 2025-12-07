#!/usr/bin/env python3
from serpapi_pool import get_key, status

print("=== TESTE POOL ===\n")

# Status inicial
s = status()
print(f"Keys: {len(s['keys'])}")
print(f"Disponíveis: {s['available']}")
print(f"Usadas: {s['used_total']}\n")

# 5 keys
print("Buscando 5 keys:\n")
for i in range(5):
    k = get_key()
    print(f"{i+1}. {k[:30]}...")

# Status final
print("\n")
s = status()
print(f"Agora disponíveis: {s['available']}")
print(f"Agora usadas: {s['used_total']}")
