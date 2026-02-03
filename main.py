from fastapi import FastAPI, Query, Path, Body
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="我的 API",
    description="这是一个示例 API，展示 FastAPI 的功能",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "开发者",
        "url": "http://example.com/contact/",
        "email": "developer@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

@app.get(
    "/users/{user_id}",
    summary="获取用户信息",
    description="根据用户 ID 获取用户的详细信息",
    response_description="用户信息对象",
    tags=["用户管理"]
)
async def get_user(
    user_id: int = Path(..., title="用户ID", description="要获取的用户ID", ge=1),
    include_posts: bool = Query(False, title="包含文章", description="是否包含用户的文章列表")
):
    """
    获取用户信息：
    
    - **user_id**: 用户的唯一标识符
    - **include_posts**: 是否在响应中包含用户的文章列表
    
    返回用户的基本信息，如果 include_posts 为 True，还会包含文章列表。
    """
    user = find_user(user_id)
    if include_posts:
        user.posts = get_user_posts(user_id)
    return user

# 自定义 OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="自定义 API 文档",
        version="2.5.0",
        description="这是自定义的 OpenAPI schema",
        routes=app.routes,
    )
    
    # 添加自定义信息
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi