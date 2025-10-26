from django.db import models
from .base import Base


class TbSecondarySchools(models.Model, Base):
    """
    香港中学信息模型
    """
    
    # 字段定义
    school_name = models.CharField(
        max_length=100,
        verbose_name='学校名称',
        help_text='学校的完整名称'
    )
    
    district = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='区域',
        help_text='学校所在的区域'
    )
    
    school_net = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='对应校网',
        help_text='学校对应的校网'
    )
    
    religion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='宗教',
        help_text='学校的宗教背景'
    )
    
    student_gender = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='学生性别',
        help_text='男/女/男女'
    )
    
    teaching_language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='授课语言',
        help_text='授课语言（中文/英文/中英并重/其他）'
    )
    
    tuition = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='学费',
        help_text='学费信息（可能包含多个说明）'
    )
    
    school_category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='学校类别',
        help_text='官立/资助/直资/私立等'
    )
    
    school_group = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='学校组别',
        help_text='学校组别（如1A、1B等）'
    )
    
    transfer_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='插班信息',
        help_text='插班申请信息'
    )
    
    total_classes = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='全校总班数',
        help_text='学校的总班级数'
    )
    
    admission_info = models.TextField(
        blank=True,
        null=True,
        verbose_name='入学信息',
        help_text='中一入学信息'
    )

    promotion_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='升学信息',
        help_text='升学信息'
    )
    
    school_curriculum = models.TextField(
        blank=True,
        null=True,
        verbose_name='课程设置',
        help_text='学校课程设置详情'
    )
    
    address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='学校地址',
        help_text='学校的详细地址'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='联系电话',
        help_text='学校联系电话'
    )
    
    email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='电子邮箱',
        help_text='学校电子邮箱'
    )
    
    website = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='官方网站',
        help_text='学校官方网站'
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
        db_table = 'tb_secondary_schools'
        verbose_name = '香港中学信息'
        verbose_name_plural = '香港中学信息'
        ordering = ['-created_at']
        
        # 添加索引
        indexes = [
            models.Index(fields=['school_name'], name='idx_sec_school_name'),
            models.Index(fields=['district'], name='idx_sec_district'),
            models.Index(fields=['school_category'], name='idx_sec_category'),
            models.Index(fields=['school_group'], name='idx_sec_group'),
            models.Index(fields=['student_gender'], name='idx_sec_gender'),
            models.Index(fields=['religion'], name='idx_sec_religion'),
            models.Index(fields=['teaching_language'], name='idx_sec_teaching_language'),
        ]
    
    def __str__(self):
        return f"{self.school_name} ({self.district})"
    
    def get_full_info(self):
        """
        获取学校的完整信息
        """
        return {
            'id': self.id,
            'school_name': self.school_name,
            'district': self.district,
            'school_net': self.school_net,
            'religion': self.religion,
            'student_gender': self.student_gender,
            'teaching_language': self.teaching_language,
            'tuition': self.tuition,
            'school_category': self.school_category,
            'school_group': self.school_group,
            'transfer_info': self.transfer_info,
            'total_classes': self.total_classes,
            'admission_info': self.admission_info,
            'promotion_info': self.promotion_info,
            'school_curriculum': self.school_curriculum,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    def is_band_one(self):
        """
        判断是否为 Band 1 学校
        """
        if self.school_group:
            return self.school_group.contains('BAND 1')
        return False
    
    def is_coed(self):
        """
        判断是否为男女校
        """
        return self.student_gender == '男女' if self.student_gender else False

