"""
错误代码和自定义异常模块
提供统一的错误代码定义和业务异常类
"""

from enum import IntEnum
from typing import Any, Optional


class ErrorCode(IntEnum):
    """
    错误代码枚举
    
    1xxx: 用户相关错误
    2xxx: 任务相关错误
    3xxx: 作业相关错误
    4xxx: 审核相关错误
    5xxx: 奖励相关错误
    6xxx: 通知相关错误
    9xxx: 系统相关错误
    """
    
    # ========== 用户相关错误 (1xxx) ==========
    USER_NOT_FOUND = 1001
    USER_ALREADY_EXISTS = 1002
    USER_INACTIVE = 1003
    INVALID_CREDENTIALS = 1004
    INVALID_TOKEN = 1005
    TOKEN_EXPIRED = 1006
    PERMISSION_DENIED = 1007
    EMAIL_ALREADY_EXISTS = 1008
    INVALID_EMAIL = 1009
    WEAK_PASSWORD = 1010
    
    # ========== 任务相关错误 (2xxx) ==========
    TASK_NOT_FOUND = 2001
    TASK_ALREADY_EXISTS = 2002
    TASK_NOT_AVAILABLE = 2003
    TASK_ALREADY_ASSIGNED = 2004
    TASK_PERMISSION_DENIED = 2005
    INVALID_TASK_STATUS = 2006
    TASK_CANNOT_BE_DELETED = 2007
    INVALID_TASK_DATA = 2008
    
    # ========== 作业相关错误 (3xxx) ==========
    ASSIGNMENT_NOT_FOUND = 3001
    ASSIGNMENT_ALREADY_EXISTS = 3002
    ASSIGNMENT_PERMISSION_DENIED = 3003
    INVALID_ASSIGNMENT_STATUS = 3004
    FILE_UPLOAD_FAILED = 3005
    INVALID_FILE_TYPE = 3006
    FILE_TOO_LARGE = 3007
    ASSIGNMENT_CANNOT_BE_UPDATED = 3008
    
    # ========== 审核相关错误 (4xxx) ==========
    REVIEW_NOT_FOUND = 4001
    REVIEW_ALREADY_EXISTS = 4002
    REVIEW_PERMISSION_DENIED = 4003
    INVALID_REVIEW_RESULT = 4004
    CANNOT_REVIEW_OWN_TASK = 4005
    REVIEW_ALREADY_COMPLETED = 4006
    APPEAL_NOT_ALLOWED = 4007
    
    # ========== 奖励相关错误 (5xxx) ==========
    REWARD_NOT_FOUND = 5001
    REWARD_ALREADY_EXISTS = 5002
    REWARD_PERMISSION_DENIED = 5003
    INVALID_REWARD_AMOUNT = 5004
    INSUFFICIENT_BALANCE = 5005
    REWARD_ALREADY_CLAIMED = 5006
    
    # ========== 通知相关错误 (6xxx) ==========
    NOTIFICATION_NOT_FOUND = 6001
    NOTIFICATION_PERMISSION_DENIED = 6002
    INVALID_NOTIFICATION_TYPE = 6003
    
    # ========== 系统相关错误 (9xxx) ==========
    INTERNAL_SERVER_ERROR = 9001
    DATABASE_ERROR = 9002
    VALIDATION_ERROR = 9003
    INVALID_PARAMETER = 9004
    MISSING_PARAMETER = 9005
    OPERATION_FAILED = 9006
    SERVICE_UNAVAILABLE = 9007
    RATE_LIMIT_EXCEEDED = 9008


class BusinessError(Exception):
    """
    业务逻辑异常类
    
    用于在业务逻辑中抛出可预期的错误，这些错误会被统一的异常处理器捕获
    并返回标准的错误响应给客户端。
    
    Attributes:
        code: 错误代码（来自 ErrorCode 枚举）
        message: 错误消息
        data: 额外的错误数据（可选）
    
    Example:
        >>> if not user:
        ...     raise BusinessError(
        ...         code=ErrorCode.USER_NOT_FOUND,
        ...         message="用户不存在"
        ...     )
    """
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        data: Optional[Any] = None
    ):
        """
        初始化业务异常
        
        Args:
            code: 错误代码
            message: 错误消息
            data: 额外的错误数据
        """
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)
    
    def __str__(self) -> str:
        """返回异常的字符串表示"""
        return f"[{self.code}] {self.message}"
    
    def to_dict(self) -> dict:
        """
        将异常转换为字典格式
        
        Returns:
            包含错误代码、消息和数据的字典
        """
        return {
            "code": int(self.code),
            "message": self.message,
            "data": self.data
        }


# 预定义的常见错误消息
ERROR_MESSAGES = {
    ErrorCode.USER_NOT_FOUND: "用户不存在",
    ErrorCode.USER_ALREADY_EXISTS: "用户已存在",
    ErrorCode.USER_INACTIVE: "用户账号已被停用",
    ErrorCode.INVALID_CREDENTIALS: "用户名或密码错误",
    ErrorCode.INVALID_TOKEN: "无效的认证令牌",
    ErrorCode.TOKEN_EXPIRED: "认证令牌已过期",
    ErrorCode.PERMISSION_DENIED: "权限不足",
    ErrorCode.EMAIL_ALREADY_EXISTS: "邮箱已被注册",
    ErrorCode.INVALID_EMAIL: "无效的邮箱地址",
    ErrorCode.WEAK_PASSWORD: "密码强度不足",
    
    ErrorCode.TASK_NOT_FOUND: "任务不存在",
    ErrorCode.TASK_ALREADY_EXISTS: "任务已存在",
    ErrorCode.TASK_NOT_AVAILABLE: "任务不可用",
    ErrorCode.TASK_ALREADY_ASSIGNED: "任务已被接取",
    ErrorCode.TASK_PERMISSION_DENIED: "无权操作此任务",
    ErrorCode.INVALID_TASK_STATUS: "无效的任务状态",
    ErrorCode.TASK_CANNOT_BE_DELETED: "任务无法删除",
    ErrorCode.INVALID_TASK_DATA: "无效的任务数据",
    
    ErrorCode.ASSIGNMENT_NOT_FOUND: "作业不存在",
    ErrorCode.ASSIGNMENT_ALREADY_EXISTS: "作业已存在",
    ErrorCode.ASSIGNMENT_PERMISSION_DENIED: "无权操作此作业",
    ErrorCode.INVALID_ASSIGNMENT_STATUS: "无效的作业状态",
    ErrorCode.FILE_UPLOAD_FAILED: "文件上传失败",
    ErrorCode.INVALID_FILE_TYPE: "不支持的文件类型",
    ErrorCode.FILE_TOO_LARGE: "文件大小超过限制",
    ErrorCode.ASSIGNMENT_CANNOT_BE_UPDATED: "作业无法更新",
    
    ErrorCode.REVIEW_NOT_FOUND: "审核记录不存在",
    ErrorCode.REVIEW_ALREADY_EXISTS: "审核记录已存在",
    ErrorCode.REVIEW_PERMISSION_DENIED: "无权进行审核",
    ErrorCode.INVALID_REVIEW_RESULT: "无效的审核结果",
    ErrorCode.CANNOT_REVIEW_OWN_TASK: "不能审核自己的任务",
    ErrorCode.REVIEW_ALREADY_COMPLETED: "审核已完成",
    ErrorCode.APPEAL_NOT_ALLOWED: "不允许申诉",
    
    ErrorCode.REWARD_NOT_FOUND: "奖励记录不存在",
    ErrorCode.REWARD_ALREADY_EXISTS: "奖励已发放",
    ErrorCode.REWARD_PERMISSION_DENIED: "无权操作奖励",
    ErrorCode.INVALID_REWARD_AMOUNT: "无效的奖励金额",
    ErrorCode.INSUFFICIENT_BALANCE: "余额不足",
    ErrorCode.REWARD_ALREADY_CLAIMED: "奖励已领取",
    
    ErrorCode.NOTIFICATION_NOT_FOUND: "通知不存在",
    ErrorCode.NOTIFICATION_PERMISSION_DENIED: "无权操作通知",
    ErrorCode.INVALID_NOTIFICATION_TYPE: "无效的通知类型",
    
    ErrorCode.INTERNAL_SERVER_ERROR: "服务器内部错误",
    ErrorCode.DATABASE_ERROR: "数据库操作失败",
    ErrorCode.VALIDATION_ERROR: "数据验证失败",
    ErrorCode.INVALID_PARAMETER: "无效的参数",
    ErrorCode.MISSING_PARAMETER: "缺少必需参数",
    ErrorCode.OPERATION_FAILED: "操作失败",
    ErrorCode.SERVICE_UNAVAILABLE: "服务暂时不可用",
    ErrorCode.RATE_LIMIT_EXCEEDED: "请求过于频繁"
}


def get_error_message(code: ErrorCode) -> str:
    """
    获取错误代码对应的默认消息
    
    Args:
        code: 错误代码
    
    Returns:
        错误消息字符串
    """
    return ERROR_MESSAGES.get(code, "未知错误")
