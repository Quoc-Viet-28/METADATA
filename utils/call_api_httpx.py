import httpx


async def get_data(url, username, password):
    async with httpx.AsyncClient(auth=httpx.DigestAuth(username, password)) as client:
        response = await client.get(url)  # Gửi yêu cầu GET
        return response
async def post_data(url, username, password, data):
    async with httpx.AsyncClient(auth=httpx.DigestAuth(username, password)) as client:
        response = await client.post(url, data=data)  # Gửi yêu cầu POST
        return response


async def post_data_auth(url, auth=None, data=None, headers=None, params=None, json=None):
    async with httpx.AsyncClient(auth=auth) as client:
        response = await client.post(url, data=data, headers=headers, params=params,json=json)  # Gửi yêu cầu POST
        return response


async def get_data_auth(url, auth=None, headers=None, params=None):
    async with httpx.AsyncClient(auth=auth) as client:
        response = await client.get(url, headers=headers, params=params)  # Gửi yêu cầu GET
        return response


