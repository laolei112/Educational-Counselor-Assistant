import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.cache import cache_page
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.models.tb_secondary_schools import TbSecondarySchools
from django.utils import timezone
import re
import json

# Cache for 1 hour (3600 seconds)
# Sitemaps don't change that often, so caching is good.
@cache_page(60 * 60)
def sitemap_view(request):
    """
    Generate dynamic sitemap.xml for SEO
    """
    # Base URL
    base_url = "https://betterschool.hk"
    
    # XML Header
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Static Pages
    static_pages = [
        '/',
        '/primary',
        '/secondary',
    ]
    
    now = timezone.now().strftime('%Y-%m-%d')
    
    # Add static pages
    for path in static_pages:
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}{path}</loc>')
        xml.append('    <changefreq>daily</changefreq>')
        xml.append('    <priority>1.0</priority>')
        xml.append(f'    <lastmod>{now}</lastmod>')
        xml.append('  </url>')

    # Dynamic Pages - Primary Schools
    # Only select ID and updated_at to be efficient
    primary_schools = TbPrimarySchools.objects.all().only('id', 'updated_at')
    for school in primary_schools:
        # Format: /school/primary/:id
        url = f"{base_url}/school/primary/{school.id}"
        last_mod = school.updated_at.strftime('%Y-%m-%d') if school.updated_at else now
        
        xml.append('  <url>')
        xml.append(f'    <loc>{url}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append(f'    <lastmod>{last_mod}</lastmod>')
        xml.append('  </url>')
        
    # Dynamic Pages - Secondary Schools
    secondary_schools = TbSecondarySchools.objects.all().only('id', 'updated_at')
    for school in secondary_schools:
        # Format: /school/secondary/:id
        url = f"{base_url}/school/secondary/{school.id}"
        last_mod = school.updated_at.strftime('%Y-%m-%d') if school.updated_at else now
        
        xml.append('  <url>')
        xml.append(f'    <loc>{url}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append(f'    <lastmod>{last_mod}</lastmod>')
        xml.append('  </url>')

    xml.append('</urlset>')
    
    return HttpResponse('\n'.join(xml), content_type="application/xml")


def get_index_html_content():
    """
    Helper to read the index.html template from various possible locations
    """
    possible_paths = [
        # Docker production path (mounted via volume)
        '/app/dist/index.html', 
        # Local dev path relative to backend/backend/api/seo_views.py -> ... -> frontend/dist
        os.path.join(settings.BASE_DIR, '../frontend/dist/index.html'),
        # Fallback relative path
        os.path.join(os.path.dirname(os.path.dirname(settings.BASE_DIR)), 'frontend/dist/index.html'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue
    return ""


def seo_school_list_view(request, school_type=None):
    """
    Server-side rendering for school list pages (/primary, /secondary)
    """
    # 1. Prepare SEO Data
    if school_type == 'primary':
        title = "全港小学排名及大全 - BetterSchool 香港好升学"
        description = "BetterSchool 提供全港小学排名、学校分区、校网、类别及学费等详细资讯，助家长为子女选择最合适的小学。"
        url = "https://betterschool.hk/primary"
        h1_text = "全港小学排名及大全"
    elif school_type == 'secondary':
        title = "全港中学排名及大全 - BetterSchool 香港好升学"
        description = "BetterSchool 提供全港中学排名、Banding、分区、校网及DSE成绩等详细资讯，助家长为子女规划升学之路。"
        url = "https://betterschool.hk/secondary"
        h1_text = "全港中学排名及大全"
    else:
        # Home or unknown
        title = "BetterSchool - 香港好升学 | 全港中小学排名及升学资讯"
        description = "BetterSchool 是您的香港好升学，提供全港中小学排名、详细学校资料、升学攻略及校网分析，助您做出明智的升学决定。"
        url = "https://betterschool.hk/"
        h1_text = "香港好升学 - BetterSchool"

    image_url = "https://betterschool.hk/favicon.jpg"

    # 2. Read Template
    html_content = get_index_html_content()
    
    if not html_content:
        return HttpResponse(f"Template not found. Please build frontend.", status=500)

    # 3. Inject Tags
    # Replace Title
    html_content = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html_content, flags=re.DOTALL)
    
    # Remove existing meta tags to avoid duplicates
    html_content = re.sub(r'<meta\s+name="description".*?>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<meta\s+property="og:.*?".*?>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<meta\s+property="twitter:.*?".*?>', '', html_content, flags=re.DOTALL)
    
    canonical_tag = f'<link rel="canonical" href="{url}" />'
    
    meta_tags = f"""
    <meta name="description" content="{description}" />
    {canonical_tag}
    
    <!-- Open Graph -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{url}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{image_url}" />
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:url" content="{url}" />
    <meta property="twitter:title" content="{title}" />
    <meta property="twitter:description" content="{description}" />
    <meta property="twitter:image" content="{image_url}" />
    """
    
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', f'{meta_tags}</head>')
    else:
        html_content += meta_tags

    # 4. Inject Body Content (Hidden H1/Desc for Crawlers)
    body_content = f"""
    <div style="position:absolute; left:-9999px; top:-9999px; width:1px; height:1px; overflow:hidden;" aria-hidden="true">
        <h1>{h1_text}</h1>
        <p>{description}</p>
        <a href="https://betterschool.hk/primary">全港小学</a>
        <a href="https://betterschool.hk/secondary">全港中学</a>
    </div>
    """
    
    if '<div id="app">' in html_content:
        html_content = html_content.replace('<div id="app">', f'<div id="app">{body_content}')
    elif '<body>' in html_content:
        html_content = html_content.replace('<body>', f'<body>{body_content}')

    return HttpResponse(html_content, content_type="text/html")


def seo_school_detail_view(request, school_type, school_id):
    """
    Server-side rendering for school detail pages to support SEO and Social Sharing.
    Injects dynamic meta tags into the index.html template.
    """
    # 1. Fetch School Data
    school = None
    try:
        if school_type == 'primary':
            school = TbPrimarySchools.objects.filter(id=school_id).first()
        elif school_type == 'secondary':
            school = TbSecondarySchools.objects.filter(id=school_id).first()
    except Exception as e:
        print(f"Error fetching school: {e}")
        pass

    # 2. Prepare SEO Data
    title = "BetterSchool - 香港好升学"
    description = "提供香港中小学详细信息、升学指导、学校对比等服务，帮助家长为孩子选择最合适的学校。"
    image_url = "https://betterschool.hk/favicon.jpg" # Default image
    url = f"https://betterschool.hk/school/{school_type}/{school_id}"

    if school:
        # Basic Info
        # Map model fields to common variables
        name = getattr(school, 'school_name', '')
        name_english = getattr(school, 'school_name_english', '') or ""
        district = getattr(school, 'district', '') or ""
        category = getattr(school, 'school_category', '') or ""
        gender = getattr(school, 'student_gender', '') or ""
        tuition = getattr(school, 'tuition', '') or ""
        school_group = getattr(school, 'school_group', '') or ""  # Band 1A, 1B等
        
        # 构建包含banding的title（SEO优化）
        title_parts = [name]
        
        # 添加英文名称（如果有）
        if name_english:
            title_parts.append(name_english)
        
        # 添加banding信息（中学特有，SEO关键）
        if school_type == 'secondary' and school_group:
            # 格式化banding：BAND 1A -> Band 1A
            banding_display = school_group.replace('BAND', 'Band').strip()
            title_parts.append(banding_display)
        elif school_type == 'secondary':
            # 如果没有具体banding，添加通用关键词
            title_parts.append("Banding")
        
        # 添加其他SEO关键词
        title_parts.append("派位 | 校網 | 排名")
        
        title = " | ".join(title_parts)
        
        # 构建包含关键词的description（SEO优化）
        desc_parts = [name]
        
        # 添加英文名称
        if name_english:
            desc_parts.append(name_english)
        
        # 添加banding信息（SEO关键）
        if school_type == 'secondary' and school_group:
            banding_display = school_group.replace('BAND', 'Band').strip()
            desc_parts.append(banding_display)
        elif school_type == 'secondary':
            desc_parts.append("Banding")
        
        # 添加其他关键信息
        if district:
            desc_parts.append(f"{district}區")
        if category:
            cat_map = {'elite': '名校联盟', 'traditional': '传统名校', 'direct': '直资', 'government': '官立', 'private': '私立'}
            desc_parts.append(cat_map.get(category, category))
        if gender:
            gender_map = {'coed': '男女校', 'boys': '男校', 'girls': '女校'}
            desc_parts.append(gender_map.get(gender, gender))
        
        # 添加长尾关键词（SEO关键）
        long_tail_keywords = "派位、校網、校風、排名、入大學、學費、入學申請、面試"
        if school_type == 'secondary':
            long_tail_keywords = f"Band、Banding、{long_tail_keywords}"
        
        description = "：".join(desc_parts) + f"。{long_tail_keywords}。查看詳細資料、升學數據、面試題目。"
        
    # 3. Read Template
    html_content = get_index_html_content()
            
    if not html_content:
        return HttpResponse("Template not found", status=500)

    # 4. Inject Tags and Content
    
    # A. Head Injection (Meta Tags)
    html_content = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<meta\s+name="description".*?>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<meta\s+property="og:.*?".*?>', '', html_content, flags=re.DOTALL)
    
    canonical_tag = f'<link rel="canonical" href="{url}" />'
    
    # Prepare JSON-LD (Structured Data)
    json_ld_data = {
        "@context": "https://schema.org",
        "@type": "School",
        "name": name if school else "BetterSchool",
        "description": description,
        "url": url,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Hong Kong",
            "addressRegion": district if school else "",
            "streetAddress": getattr(school, 'address', '') or district if school else ""
        }
    }
    if school:
        # 添加英文名称
        if name_english:
            json_ld_data["alternateName"] = name_english
        
        # 添加banding信息（中学特有）
        if school_type == 'secondary' and school_group:
            json_ld_data["identifier"] = {
                "@type": "PropertyValue",
                "name": "School Banding",
                "value": school_group.replace('BAND', 'Band').strip()
            }
        
        if hasattr(school, 'phone') and school.phone:
            json_ld_data["telephone"] = school.phone
        if hasattr(school, 'website') and school.website:
            json_ld_data["sameAs"] = school.website
        if tuition:
             json_ld_data["priceRange"] = tuition
         
    json_ld_script = f'<script type="application/ld+json">{json.dumps(json_ld_data, ensure_ascii=False)}</script>'
    
    meta_tags = f"""
    <meta name="description" content="{description}" />
    {canonical_tag}
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{url}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{image_url}" />
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:url" content="{url}" />
    <meta property="twitter:title" content="{title}" />
    <meta property="twitter:description" content="{description}" />
    <meta property="twitter:image" content="{image_url}" />
    
    {json_ld_script}
    """
    
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', f'{meta_tags}</head>')
    else:
        html_content += meta_tags

    # B. Body Injection (Visible Content for Crawlers)
    features_html = ""
    if school and hasattr(school, 'features') and school.features:
        feats = school.features if isinstance(school.features, list) else []
        if feats:
            features_html = "<ul>" + "".join([f"<li>{f}</li>" for f in feats]) + "</ul>"
            
    # 构建包含更多关键词的隐藏SEO内容
    banding_info = ""
    school_group_val = ""
    if school and school_type == 'secondary':
        school_group_val = getattr(school, 'school_group', '') or ""
        if school_group_val:
            banding_display = school_group_val.replace('BAND', 'Band').strip()
            banding_info = f'<h2>{name} Banding</h2><h2>{name} Band</h2><p>{name} {banding_display}</p>'
        else:
            banding_info = f'<h2>{name} Banding</h2><h2>{name} Band</h2>'
    
    # 构建长尾关键词段落
    long_tail_text = ""
    if school and name:
        keywords_list = [
            f"{name} 派位",
            f"{name} 校網",
            f"{name} 校風",
            f"{name} 排名",
            f"{name} 入大學",
            f"{name} 學費",
            f"{name} 入學申請",
            f"{name} 面試"
        ]
        if school_type == 'secondary':
            keywords_list.insert(0, f"{name} Banding")
            keywords_list.insert(1, f"{name} Band")
        long_tail_text = f'<p>{"、".join(keywords_list)}</p>'
    
    # 构建Band信息（如果有）
    band_dt_dd = ""
    if school and school_type == 'secondary':
        band_value = school_group_val if school_group_val else "未分类"
        band_dt_dd = f'<dt>Band</dt><dd>{band_value}</dd>'
    
    body_content = f"""
    <div style="position:absolute; left:-9999px; top:-9999px; width:1px; height:1px; overflow:hidden;" aria-hidden="true">
        <h1>{name if school else title}</h1>
        {banding_info}
        <p>{description}</p>
        <dl>
            <dt>区域</dt><dd>{district if school else ''}</dd>
            <dt>类别</dt><dd>{category if school else ''}</dd>
            {band_dt_dd}
            <dt>学费</dt><dd>{tuition if school else ''}</dd>
            <dt>地址</dt><dd>{getattr(school, 'address', '') if school else ''}</dd>
        </dl>
        {long_tail_text}
        {features_html}
        <a href="{url}">查看详情</a>
    </div>
    """
    
    if '<div id="app">' in html_content:
        html_content = html_content.replace('<div id="app">', f'<div id="app">{body_content}')
    elif '<body>' in html_content:
        html_content = html_content.replace('<body>', f'<body>{body_content}')

    return HttpResponse(html_content, content_type="text/html")
