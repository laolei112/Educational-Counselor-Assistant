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
        district = getattr(school, 'district', '') or ""
        category = getattr(school, 'school_category', '') or ""
        gender = getattr(school, 'student_gender', '') or ""
        tuition = getattr(school, 'tuition', '') or ""
        
        title = f"{name} - BetterSchool 香港好升学"
        
        # Construct a rich description
        desc_parts = []
        if district: desc_parts.append(district)
        cat_map = {'elite': '名校联盟', 'traditional': '传统名校', 'direct': '直资', 'government': '官立', 'private': '私立'}
        desc_parts.append(cat_map.get(category, category))
        
        if gender:
            gender_map = {'coed': '男女校', 'boys': '男校', 'girls': '女校'}
            desc_parts.append(gender_map.get(gender, gender))
            
        if tuition:
            desc_parts.append(f"学费: {tuition}")
            
        description = f"查看{name}的详细资料：{' | '.join(desc_parts)}。提供全面的升学数据、面试题目、入学申请资讯。"
        
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
            
    body_content = f"""
    <div style="position:absolute; left:-9999px; top:-9999px; width:1px; height:1px; overflow:hidden;" aria-hidden="true">
        <h1>{name if school else title}</h1>
        <p>{description}</p>
        <dl>
            <dt>区域</dt><dd>{district if school else ''}</dd>
            <dt>类别</dt><dd>{category if school else ''}</dd>
            <dt>学费</dt><dd>{tuition if school else ''}</dd>
            <dt>地址</dt><dd>{getattr(school, 'address', '') if school else ''}</dd>
        </dl>
        {features_html}
        <a href="{url}">查看详情</a>
    </div>
    """
    
    if '<div id="app">' in html_content:
        html_content = html_content.replace('<div id="app">', f'<div id="app">{body_content}')
    elif '<body>' in html_content:
        html_content = html_content.replace('<body>', f'<body>{body_content}')

    return HttpResponse(html_content, content_type="text/html")
