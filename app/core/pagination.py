"""
分页辅助工具模块
提供通用的分页查询和响应构造功能
"""

from typing import TypeVar, Generic, List, Optional
from math import ceil
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func


T = TypeVar('T')


class PageParams(BaseModel):
    """
    分页参数模型
    
    Attributes:
        page: 当前页码（从 1 开始）
        page_size: 每页大小
        order_by: 排序字段（可选）
        order_desc: 是否降序排序
    """
    page: int = 1
    page_size: int = 10
    order_by: Optional[str] = None
    order_desc: bool = False
    
    def get_offset(self) -> int:
        """计算 SQL OFFSET 值"""
        return (self.page - 1) * self.page_size
    
    def get_limit(self) -> int:
        """获取 SQL LIMIT 值"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应模型
    
    Attributes:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页大小
        total_pages: 总页数
        has_next: 是否有下一页
        has_prev: 是否有上一页
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    class Config:
        arbitrary_types_allowed = True


def paginate(
    db: Session,
    query,
    page: int = 1,
    page_size: int = 10,
    max_page_size: int = 100
) -> tuple:
    """
    执行分页查询（通用版本）
    
    Args:
        db: 数据库会话
        query: SQLAlchemy 查询对象
        page: 页码（从 1 开始）
        page_size: 每页大小
        max_page_size: 每页最大记录数
    
    Returns:
        (items, total) 元组：当前页数据列表和总记录数
    
    Example:
        >>> query = select(User).where(User.is_active == True)
        >>> items, total = paginate(db, query, page=1, page_size=10)
        >>> return paginated_response(items, total, 1, 10)
    """
    # 限制 page_size 的最大值
    page_size = min(page_size, max_page_size)
    
    # 确保 page 至少为 1
    page = max(1, page)
    
    # 计算 offset
    offset = (page - 1) * page_size
    
    # 查询总数
    total = db.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar()
    
    # 查询当前页数据
    items = db.execute(
        query.offset(offset).limit(page_size)
    ).scalars().all()
    
    return items, total


def create_paginated_response(
    items: List[T],
    total: int,
    page: int,
    page_size: int
) -> PaginatedResponse[T]:
    """
    创建分页响应对象
    
    Args:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页大小
    
    Returns:
        PaginatedResponse 对象
    
    Example:
        >>> items, total = paginate(db, query, page=1, page_size=10)
        >>> response = create_paginated_response(items, total, 1, 10)
        >>> return success_response(data=response.dict())
    """
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


def paginate_query_result(
    items: List[T],
    total: int,
    page: int,
    page_size: int
) -> dict:
    """
    将分页结果转换为字典格式（用于直接返回）
    
    Args:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页大小
    
    Returns:
        包含分页信息的字典
    
    Example:
        >>> items, total = paginate(db, query, page=1, page_size=10)
        >>> data = paginate_query_result(items, total, 1, 10)
        >>> return success_response(data=data)
    """
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


class PaginationHelper:
    """
    分页辅助类（面向对象版本）
    
    使用示例：
        >>> helper = PaginationHelper(db, page=1, page_size=10)
        >>> query = select(User).where(User.is_active == True)
        >>> result = helper.paginate(query)
        >>> return success_response(data=result)
    """
    
    def __init__(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 10,
        max_page_size: int = 100
    ):
        """
        初始化分页助手
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页大小
            max_page_size: 每页最大记录数
        """
        self.db = db
        self.page = max(1, page)
        self.page_size = min(page_size, max_page_size)
        self.max_page_size = max_page_size
    
    def get_offset(self) -> int:
        """计算 OFFSET 值"""
        return (self.page - 1) * self.page_size
    
    def paginate(self, query) -> dict:
        """
        执行分页查询并返回结果
        
        Args:
            query: SQLAlchemy 查询对象
        
        Returns:
            包含分页数据和元信息的字典
        """
        # 查询总数
        total = self.db.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar()
        
        # 查询当前页数据
        items = self.db.execute(
            query.offset(self.get_offset()).limit(self.page_size)
        ).scalars().all()
        
        return paginate_query_result(items, total, self.page, self.page_size)
