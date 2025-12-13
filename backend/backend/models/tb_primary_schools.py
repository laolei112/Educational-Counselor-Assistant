from django.db import models
from .base import Base


class TbPrimarySchools(models.Model, Base):
    """
    香港小学信息模型
    """
    
    # 基本信息字段
    school_name = models.CharField(
        max_length=100,
        verbose_name='学校名称',
        help_text='学校的完整名称'
    )
    
    # 多语言字段
    school_name_traditional = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='学校名称（繁体）',
        help_text='学校的繁体名称'
    )
    
    school_name_english = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='学校名称（英文）',
        help_text='学校的英文名称'
    )
    
    district = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='区域',
        help_text='学校所在的区域'
    )
    
    school_net = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='小一学校网',
        help_text='小一学校网'
    )
    
    address = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='学校地址',
        help_text='学校的详细地址'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='学校电话',
        help_text='学校联系电话'
    )
    
    fax = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='学校传真',
        help_text='学校传真号码'
    )
    
    email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='学校电邮',
        help_text='学校电子邮箱'
    )
    
    website = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='学校网址',
        help_text='学校官方网站'
    )
    
    # 学校分类
    school_category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='学校类别',
        help_text='资助/直资/私立/官立'
    )
    
    school_category_2 = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='学校类别2',
        help_text='全日/半日'
    )
    
    student_gender = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='学生性别',
        help_text='男/女/男女'
    )
    
    religion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='宗教',
        help_text='学校的宗教背景'
    )
    
    teaching_language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='教学语言',
        help_text='教学语言（中文/英文/中英并重/其他）'
    )
    
    # ========== 新增字段 - 基本信息 ==========
    school_sponsor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='办学团体',
        help_text='办学团体名称'
    )
    
    founded_year = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='创校年份',
        help_text='学校创办年份'
    )
    
    school_motto = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='校训',
        help_text='学校校训'
    )
    
    school_area = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='学校占地面积',
        help_text='学校占地面积'
    )
    
    # ========== 新增字段 - 教师信息 ==========
    teacher_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='教师总人数',
        help_text='学校教师总人数'
    )
    
    teacher_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='教师信息',
        help_text='教师学历和经验比例信息，JSON格式'
    )
    
    # ========== 新增字段 - 设施信息 ==========
    classroom_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='课室数目',
        help_text='学校课室数量'
    )
    
    hall_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='礼堂数目',
        help_text='学校礼堂数量'
    )
    
    playground_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='操场数目',
        help_text='学校操场数量'
    )
    
    library_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='图书馆数目',
        help_text='学校图书馆数量'
    )
    
    special_rooms = models.TextField(
        blank=True,
        null=True,
        verbose_name='特别室',
        help_text='学校特别室设施'
    )
    
    # ========== 新增字段 - 交通信息 ==========
    school_bus = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='校车',
        help_text='校车服务'
    )
    
    nanny_bus = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='保姆车',
        help_text='保姆车服务'
    )
    
    # ========== 新增字段 - 班级信息 ==========
    classes_by_grade = models.JSONField(
        blank=True,
        null=True,
        verbose_name='各年级班数',
        help_text='各年级班级数量，JSON格式'
    )
    
    class_teaching_mode = models.TextField(
        blank=True,
        null=True,
        verbose_name='班级教学模式',
        help_text='班级教学模式说明'
    )
    
    # ========== 新增字段 - 评估信息 ==========
    assessment_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='学习评估信息',
        help_text='测验考试安排、评估政策等信息'
    )
    
    multi_assessment = models.TextField(
        blank=True,
        null=True,
        verbose_name='多元学习评估',
        help_text='多元学习评估方式'
    )
    
    class_arrangement = models.TextField(
        blank=True,
        null=True,
        verbose_name='分班安排',
        help_text='学校分班安排说明'
    )
    
    # ========== 新增字段 - 学校生活 ==========
    lunch_arrangement = models.TextField(
        blank=True,
        null=True,
        verbose_name='午膳安排',
        help_text='学校午膳安排'
    )
    
    school_life_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='学校生活备注',
        help_text='学校生活相关备注'
    )
    
    # ========== 新增字段 - 学校特色 ==========
    whole_person_learning = models.TextField(
        blank=True,
        null=True,
        verbose_name='全方位学习',
        help_text='学校的全方位学习活动'
    )
    
    school_mission = models.TextField(
        blank=True,
        null=True,
        verbose_name='办学宗旨',
        help_text='学校的办学宗旨'
    )
    
    diversity_support = models.TextField(
        blank=True,
        null=True,
        verbose_name='照顾学生多样性',
        help_text='全校参与照顾学生的多样性措施'
    )
    
    # JSON 字段（保留原有）
    school_basic_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='学校基础信息',
        help_text='学校基础信息（办学团体、创校年份、校训、占地面积、交通等）'
    )
    
    secondary_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='中学联系信息',
        help_text='一条龙中学、直属中学、联系中学等信息'
    )
    
    tuition = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='学费',
        help_text='学费信息'
    )
    
    # 总班数（或小六学生估算数），用于快速统计/展示
    total_classes = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='总班数',
        help_text='学校总班数或对应估算数值（来源于数据汇总）'
    )
    
    # Band 1比例（生成列，从promotion_info JSON中提取，用于排序和筛选优化）
    # 注意：这是数据库生成列，通过SQL创建，Django只用于查询
    band1_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='升Band 1比例',
        help_text='升Band 1比例（从promotion_info JSON中提取的生成列，用于性能优化）',
        db_column='band1_rate'
    )
    
    total_classes_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='总班数信息',
        help_text='各年级班数及总班数信息'
    )
    
    class_teaching_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='班级教学信息',
        help_text='班级教学模式、分班安排等信息'
    )
    
    transfer_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='插班信息',
        help_text='插班申请信息'
    )

    promotion_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='升学信息',
        help_text='升学信息'
    )
    
    # 系统字段
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'tb_primary_schools'
        verbose_name = '香港小学信息'
        verbose_name_plural = '香港小学信息'
        ordering = ['-created_at']
        
        # 添加索引
        indexes = [
            models.Index(fields=['school_name'], name='idx_pri_school_name'),
            models.Index(fields=['district'], name='idx_pri_district'),
            models.Index(fields=['school_net'], name='idx_pri_school_net'),
            models.Index(fields=['school_category'], name='idx_pri_category'),
            models.Index(fields=['student_gender'], name='idx_pri_gender'),
            models.Index(fields=['religion'], name='idx_pri_religion'),
            models.Index(fields=['teaching_language'], name='idx_pri_teaching_lang'),
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
            'address': self.address,
            'phone': self.phone,
            'fax': self.fax,
            'email': self.email,
            'website': self.website,
            'school_category': self.school_category,
            'school_category_2': self.school_category_2,
            'student_gender': self.student_gender,
            'religion': self.religion,
            'teaching_language': self.teaching_language,
            # 新增字段
            'school_sponsor': self.school_sponsor,
            'founded_year': self.founded_year,
            'school_motto': self.school_motto,
            'school_area': self.school_area,
            'teacher_count': self.teacher_count,
            'teacher_info': self.teacher_info,
            'classroom_count': self.classroom_count,
            'hall_count': self.hall_count,
            'playground_count': self.playground_count,
            'library_count': self.library_count,
            'special_rooms': self.special_rooms,
            'school_bus': self.school_bus,
            'nanny_bus': self.nanny_bus,
            'classes_by_grade': self.classes_by_grade,
            'class_teaching_mode': self.class_teaching_mode,
            'assessment_info': self.assessment_info,
            'multi_assessment': self.multi_assessment,
            'class_arrangement': self.class_arrangement,
            'lunch_arrangement': self.lunch_arrangement,
            'school_life_notes': self.school_life_notes,
            'whole_person_learning': self.whole_person_learning,
            'school_mission': self.school_mission,
            'diversity_support': self.diversity_support,
            # 原有字段
            'school_basic_info': self.school_basic_info,
            'secondary_info': self.secondary_info,
            'tuition': self.tuition,
            'total_classes_info': self.total_classes_info,
            'class_teaching_info': self.class_teaching_info,
            'transfer_info': self.transfer_info,
            'promotion_info': self.promotion_info,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    def get_total_classes(self):
        """
        获取总班数
        """
        if self.total_classes_info and 'current_year_total_classes' in self.total_classes_info:
            return self.total_classes_info['current_year_total_classes']
        return self.total_classes
    
    def get_linked_secondary_schools(self):
        """
        获取关联的中学
        """
        if not self.secondary_info:
            return []
        
        schools = []
        if self.secondary_info.get('through_train'):
            schools.extend([{'name': s, 'type': '一条龙'} for s in self.secondary_info['through_train'].split('、') if s and s != '-'])
        if self.secondary_info.get('direct'):
            schools.extend([{'name': s, 'type': '直属'} for s in self.secondary_info['direct'].split('、') if s and s != '-'])
        if self.secondary_info.get('associated'):
            schools.extend([{'name': s, 'type': '联系'} for s in self.secondary_info['associated'].split('、') if s and s != '-'])
        
        return schools
    
    def is_full_day(self):
        """
        判断是否为全日制
        """
        if self.school_category_2:
            return self.school_category_2 == '全日'
        if self.school_basic_info and 'school_category_2' in self.school_basic_info:
            return self.school_basic_info['school_category_2'] == '全日'
        return False
    
    def is_coed(self):
        """
        判断是否为男女校
        """
        return self.student_gender == '男女' if self.student_gender else False

