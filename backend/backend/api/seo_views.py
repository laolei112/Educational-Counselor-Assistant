import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.cache import cache_page
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.models.tb_secondary_schools import TbSecondarySchools
from django.utils import timezone

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
    title = "BetterSchool - 香港升学助手"
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
        
        # Convert category for better readability if needed, or keep as is.
        # Just simple concatenation for description.
        
        title = f"{name} - BetterSchool 香港升学助手"
        
        # Construct a rich description
        # Example: "查看 St. Paul's Co-educational College 的详细资料：中西区 | 直资 | 男女校 | 学费: $65,800 | Band 1A ..."
        desc_parts = []
        if district: desc_parts.append(district)
        # Mapping category to Chinese label if stored in English (simple check)
        cat_map = {'elite': '名校联盟', 'traditional': '传统名校', 'direct': '直资', 'government': '官立', 'private': '私立'}
        desc_parts.append(cat_map.get(category, category))
        
        if gender:
            gender_map = {'coed': '男女校', 'boys': '男校', 'girls': '女校'}
            desc_parts.append(gender_map.get(gender, gender))
            
        if tuition:
            desc_parts.append(f"学费: {tuition}")
            
        description = f"查看{name}的详细资料：{' | '.join(desc_parts)}。提供全面的升学数据、面试题目、入学申请资讯。"
        
        # If school has specific image, use it (optional)
    
    # 3. Read Template (dist/index.html)
    # Try to find the file in possible locations
    possible_paths = [
        # Docker production path (mounted via volume)
        '/app/dist/index.html', 
        # Local dev path relative to backend/backend/api/seo_views.py -> ... -> frontend/dist
        os.path.join(settings.BASE_DIR, '../frontend/dist/index.html'),
        # Fallback relative path
        os.path.join(os.path.dirname(os.path.dirname(settings.BASE_DIR)), 'frontend/dist/index.html'),
    ]
    
    html_content = ""
    found_path = ""
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                found_path = path
                break
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue
            
    if not html_content:
        # Fallback HTML if index.html is not found
        return HttpResponse(f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8" />
            <title>{title}</title>
            <meta name="description" content="{description}" />
            <meta property="og:title" content="{title}" />
            <meta property="og:description" content="{description}" />
            <meta property="og:image" content="{image_url}" />
            <meta property="og:url" content="{url}" />
            <meta name="robots" content="index, follow" />
        </head>
        <body>
            <h1>{title}</h1>
            <p>{description}</p>
            <p>正在加载完整内容...</p>
            <script>window.location.reload()</script>
        </body>
        </html>
        """, content_type="text/html")

    # 4. Inject Tags
    # We replace the default title and inject meta tags before </head>
    
    # Replace Title
    # Handles <title>BetterSchool</title> or other variations
    import re
    # Use DOTALL to match across newlines just in case
    html_content = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html_content, flags=re.DOTALL)
    
    # Remove existing meta description and og tags to avoid duplicates
    html_content = re.sub(r'<meta\s+name="description".*?>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<meta\s+property="og:.*?".*?>', '', html_content, flags=re.DOTALL)
    
    # New Meta Tags
    meta_tags = f"""
    <meta name="description" content="{description}" />
    
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
    """
    
    # Insert before </head>
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', f'{meta_tags}</head>')
    else:
        # If for some reason no head tag
        html_content += meta_tags

    return HttpResponse(html_content, content_type="text/html")

