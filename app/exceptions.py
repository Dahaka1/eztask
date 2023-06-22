from fastapi import HTTPException, status


class CredentialsException(HTTPException):
	"""
	authorizing by Bearer token error
	"""
	def __init__(self, detail: str = "Could not validate credentials"):
		self.status_code = status.HTTP_401_UNAUTHORIZED
		self.headers = {"WWW-Authenticate": "Bearer"}
		self.detail = detail
