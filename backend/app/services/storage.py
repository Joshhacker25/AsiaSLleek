"""Media storage adapter. Local dev uses a mock: no real media is stored.
Replace MockStorage with a real provider (S3-compatible/CDN) via env vars.
"""
import os
class MockStorage:
    configured = False
    def save(self, filename, content=b""):
        return {"stored": False, "mock": True, "filename": filename, "note": "Mock storage only; no file saved."}
    def url(self, filename):
        return ""
def get_storage():
    return MockStorage()
