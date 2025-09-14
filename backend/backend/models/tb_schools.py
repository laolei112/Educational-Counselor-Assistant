from django.db import models
from .base import Base


class TbSchools(Base):
    """
    学校信息模型
    """    
    # 学校分类选择
    CATEGORY_CHOICES = [
        ('elite', '精英学校'),
        ('traditional', '传统学校'),
        ('direct', '直资学校'),
        ('government', '政府学校'),
        ('private', '私立学校'),
    ]
    
    # 性别选择
    GENDER_CHOICES = [
        ('coed', '男女校'),
        ('boys', '男校'),
        ('girls', '女校'),
    ]
    
    # 申请状态选择
    APPLICATION_STATUS_CHOICES = [
        ('open', '开放申请'),
        ('closed', '关闭申请'),
        ('deadline', '截止申请'),
    ]
    
    # 学校级别选择
    LEVEL_CHOICES = [
        ('primary', '小学'),
        ('secondary', '中学'),
    ]
    
    # 字段定义
    name = models.CharField(
        max_length=255, 
        verbose_name='学校名称',
        help_text='学校的完整名称'
    )
    
    url = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name='学校信息页面URL',
        help_text='学校在 schooland.hk 的页面链接'
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True,
        verbose_name='学校分类',
        help_text='学校的分类类型'
    )
    
    net_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='校网',
        help_text='所属校网'
    )
    
    religion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='宗教背景',
        help_text='学校的宗教背景'
    )
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='性别',
        help_text='男女校/男校/女校'
    )
    
    address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='学校地址',
        help_text='学校的详细地址'
    )
    
    district = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='所属地区',
        help_text='学校所在的地区'
    )
    
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        verbose_name='学校级别',
        help_text='学校的级别'
    )
    
    official_website = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='官方网站',
        help_text='学校的官方网站'
    )
    
    promotion_rate = models.JSONField(
        blank=True,
        null=True,
        verbose_name='升学比例',
        help_text='升学比例数据(JSON格式)'
    )
    
    application_status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default='open',
        verbose_name='申请状态',
        help_text='当前的申请状态'
    )
    
    tuition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='学费',
        help_text='学校学费（港币）'
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注',
        help_text='其他备注信息'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'tb_schools'
        verbose_name = '学校信息'
        verbose_name_plural = '学校信息'
        ordering = ['-created_at']
        
        # 添加索引
        indexes = [
            models.Index(fields=['level'], name='idx_level'),
            models.Index(fields=['district'], name='idx_district'),
            models.Index(fields=['category'], name='idx_category'),
            models.Index(fields=['gender'], name='idx_gender'),
            models.Index(fields=['application_status'], name='idx_application_status'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"
    
    def get_full_info(self):
        """
        获取学校的完整信息
        """
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'category': self.category,
            'district': self.district,
            'gender': self.gender,
            'application_status': self.application_status,
            'tuition': float(self.tuition) if self.tuition else 0,
            'official_website': self.official_website,
            'address': self.address,
            'net_name': self.net_name,
            'religion': self.religion,
            'promotion_rate': self.promotion_rate,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    def is_primary_school(self):
        """
        判断是否为小学
        """
        return self.level == 'primary'
    
    def is_secondary_school(self):
        """
        判断是否为中学
        """
        return self.level == 'secondary'
    
    def is_application_open(self):
        """
        判断申请是否开放
        """
        return self.application_status == 'open'
