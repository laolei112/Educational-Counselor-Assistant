# ============================================
# MySQL 数据库性能诊断和优化工具
# ============================================

from django.db import connection
from django.core.management.base import BaseCommand
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.models.tb_secondary_schools import TbSecondarySchools
import time
import json


class MySQLDiagnostics:
    """MySQL 性能诊断工具"""
    
    def __init__(self):
        self.results = {}
    
    def print_header(self, title):
        """打印标题"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_section(self, title):
        """打印小节标题"""
        print(f"\n[{title}]")
        print("-" * 80)
    
    def diagnose_all(self):
        """执行所有诊断"""
        self.check_mysql_version()
        self.check_table_status()
        self.check_table_fragmentation()
        self.check_indexes()
        self.check_index_cardinality()
        self.analyze_count_performance()
        self.check_mysql_config()
        self.check_slow_queries()
        self.check_table_locks()
        self.generate_optimization_recommendations()
        
        return self.results
    
    def check_mysql_version(self):
        """检查 MySQL 版本"""
        self.print_header("1. MySQL 版本信息")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"MySQL 版本: {version}")
            
            cursor.execute("SELECT @@sql_mode")
            sql_mode = cursor.fetchone()[0]
            print(f"SQL 模式: {sql_mode}")
            
            self.results['version'] = {
                'version': version,
                'sql_mode': sql_mode
            }
    
    def check_table_status(self):
        """检查表状态"""
        self.print_header("2. 表状态信息")
        
        tables = ['tb_primary_schools', 'tb_secondary_schools']
        
        with connection.cursor() as cursor:
            for table in tables:
                self.print_section(f"表: {table}")
                
                cursor.execute(f"""
                    SELECT 
                        TABLE_NAME,
                        ENGINE,
                        TABLE_ROWS,
                        AVG_ROW_LENGTH,
                        ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
                        ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS index_mb,
                        ROUND(DATA_FREE / 1024 / 1024, 2) AS free_mb,
                        TABLE_COLLATION,
                        CREATE_TIME,
                        UPDATE_TIME,
                        CHECK_TIME
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                """, [table])
                
                result = cursor.fetchone()
                if result:
                    print(f"  存储引擎: {result[1]}")
                    print(f"  估算行数: {result[2]:,}")
                    print(f"  平均行长: {result[3]} bytes")
                    print(f"  数据大小: {result[4]} MB")
                    print(f"  索引大小: {result[5]} MB")
                    print(f"  空闲空间: {result[6]} MB")
                    print(f"  字符集: {result[7]}")
                    print(f"  创建时间: {result[8]}")
                    print(f"  更新时间: {result[9]}")
                    print(f"  检查时间: {result[10]}")
                    
                    if not self.results.get('tables'):
                        self.results['tables'] = {}
                    
                    self.results['tables'][table] = {
                        'engine': result[1],
                        'rows': result[2],
                        'avg_row_length': result[3],
                        'data_mb': result[4],
                        'index_mb': result[5],
                        'free_mb': result[6]
                    }
    
    def check_table_fragmentation(self):
        """检查表碎片"""
        self.print_header("3. 表碎片分析")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    TABLE_NAME,
                    ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
                    ROUND(DATA_FREE / 1024 / 1024, 2) AS free_mb,
                    ROUND(DATA_FREE / (DATA_LENGTH + INDEX_LENGTH) * 100, 2) AS fragmentation_pct
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME IN ('tb_primary_schools', 'tb_secondary_schools')
                ORDER BY fragmentation_pct DESC
            """)
            
            results = cursor.fetchall()
            for row in results:
                table_name, data_mb, free_mb, frag_pct = row
                status = "✗ 需要优化" if frag_pct > 10 else "✓ 良好"
                print(f"  {table_name:30s} | 数据: {data_mb:8.2f}MB | "
                      f"碎片: {free_mb:8.2f}MB ({frag_pct:5.2f}%) | {status}")
                
                if not self.results.get('fragmentation'):
                    self.results['fragmentation'] = {}
                
                self.results['fragmentation'][table_name] = {
                    'data_mb': data_mb,
                    'free_mb': free_mb,
                    'fragmentation_pct': frag_pct,
                    'needs_optimize': frag_pct > 10
                }
    
    def check_indexes(self):
        """检查索引"""
        self.print_header("4. 索引信息")
        
        tables = ['tb_primary_schools', 'tb_secondary_schools']
        
        with connection.cursor() as cursor:
            for table in tables:
                self.print_section(f"表: {table}")
                
                cursor.execute("""
                    SELECT 
                        INDEX_NAME,
                        NON_UNIQUE,
                        SEQ_IN_INDEX,
                        COLUMN_NAME,
                        COLLATION,
                        CARDINALITY,
                        INDEX_TYPE,
                        COMMENT
                    FROM information_schema.STATISTICS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    ORDER BY INDEX_NAME, SEQ_IN_INDEX
                """, [table])
                
                results = cursor.fetchall()
                current_index = None
                index_columns = []
                
                for row in results:
                    idx_name, non_unique, seq, col_name, collation, cardinality, idx_type, comment = row
                    
                    if current_index != idx_name:
                        if current_index:
                            print(f"    列: {', '.join(index_columns)}")
                        
                        unique_str = "UNIQUE" if non_unique == 0 else "NON-UNIQUE"
                        print(f"\n  索引: {idx_name} ({unique_str}, {idx_type})")
                        current_index = idx_name
                        index_columns = []
                    
                    index_columns.append(col_name)
                    print(f"    [{seq}] {col_name:30s} | 基数: {cardinality or 'N/A':>10}")
                
                if index_columns:
                    print(f"    列: {', '.join(index_columns)}")
    
    def check_index_cardinality(self):
        """检查索引基数 (选择性)"""
        self.print_header("5. 索引选择性分析")
        
        print("\n索引选择性 = CARDINALITY / TABLE_ROWS")
        print("选择性越高(接近1),索引效果越好")
        print("选择性 < 0.1 的索引可能效果不佳\n")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s.TABLE_NAME,
                    s.INDEX_NAME,
                    s.CARDINALITY,
                    t.TABLE_ROWS,
                    ROUND(s.CARDINALITY / t.TABLE_ROWS, 4) AS selectivity
                FROM information_schema.STATISTICS s
                JOIN information_schema.TABLES t 
                    ON s.TABLE_SCHEMA = t.TABLE_SCHEMA 
                    AND s.TABLE_NAME = t.TABLE_NAME
                WHERE s.TABLE_SCHEMA = DATABASE()
                AND s.TABLE_NAME IN ('tb_primary_schools', 'tb_secondary_schools')
                AND s.SEQ_IN_INDEX = 1
                AND t.TABLE_ROWS > 0
                ORDER BY selectivity ASC
            """)
            
            results = cursor.fetchall()
            for row in results:
                table, index, cardinality, total_rows, selectivity = row
                if selectivity:
                    status = "✗ 差" if selectivity < 0.1 else "⚠ 中" if selectivity < 0.5 else "✓ 好"
                    print(f"  {table:30s} | {index:25s} | "
                          f"选择性: {selectivity:6.4f} | {status}")
    
    def analyze_count_performance(self):
        """分析 COUNT 查询性能"""
        self.print_header("6. COUNT 查询性能测试")
        
        tests = [
            ("无过滤条件", "SELECT COUNT(*) FROM tb_primary_schools"),
            ("简单过滤 (district)", "SELECT COUNT(*) FROM tb_primary_schools WHERE district = '中西區'"),
            ("复合过滤", "SELECT COUNT(*) FROM tb_primary_schools WHERE district = '中西區' AND school_category = '資助'"),
            ("带 ORDER BY (错误示例)", "SELECT COUNT(*) FROM tb_primary_schools ORDER BY band1_rate DESC"),
        ]
        
        with connection.cursor() as cursor:
            for test_name, sql in tests:
                self.print_section(test_name)
                
                # 测试 5 次取平均值
                times = []
                for i in range(5):
                    start = time.time()
                    cursor.execute(sql)
                    result = cursor.fetchone()[0]
                    elapsed = (time.time() - start) * 1000
                    times.append(elapsed)
                
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                status = "✓ 快" if avg_time < 50 else "⚠ 中" if avg_time < 200 else "✗ 慢"
                
                print(f"  SQL: {sql}")
                print(f"  结果: {result:,} 行")
                print(f"  平均耗时: {avg_time:.2f}ms | 最小: {min_time:.2f}ms | 最大: {max_time:.2f}ms | {status}")
                
                # 查看执行计划
                cursor.execute(f"EXPLAIN {sql}")
                explain = cursor.fetchone()
                print(f"  执行计划: {explain}")
                
                if not self.results.get('count_performance'):
                    self.results['count_performance'] = {}
                
                self.results['count_performance'][test_name] = {
                    'avg_ms': avg_time,
                    'min_ms': min_time,
                    'max_ms': max_time,
                    'result': result
                }
    
    def check_mysql_config(self):
        """检查 MySQL 配置"""
        self.print_header("7. MySQL 配置检查")
        
        important_vars = [
            'innodb_buffer_pool_size',
            'innodb_log_file_size',
            'innodb_flush_log_at_trx_commit',
            'max_connections',
            'query_cache_size',
            'query_cache_type',
            'tmp_table_size',
            'max_heap_table_size',
            'sort_buffer_size',
            'join_buffer_size',
            'thread_cache_size'
        ]
        
        with connection.cursor() as cursor:
            for var_name in important_vars:
                try:
                    cursor.execute(f"SHOW VARIABLES LIKE '{var_name}'")
                    result = cursor.fetchone()
                    if result:
                        print(f"  {result[0]:35s} = {result[1]}")
                        
                        if not self.results.get('mysql_config'):
                            self.results['mysql_config'] = {}
                        
                        self.results['mysql_config'][result[0]] = result[1]
                except:
                    pass
    
    def check_slow_queries(self):
        """检查慢查询配置"""
        self.print_header("8. 慢查询日志配置")
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW VARIABLES LIKE 'slow_query%'")
            results = cursor.fetchall()
            
            for var_name, var_value in results:
                print(f"  {var_name:35s} = {var_value}")
            
            cursor.execute("SHOW VARIABLES LIKE 'long_query_time'")
            result = cursor.fetchone()
            if result:
                print(f"  {result[0]:35s} = {result[1]} 秒")
    
    def check_table_locks(self):
        """检查表锁和正在运行的查询"""
        self.print_header("9. 当前运行的查询")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    ID,
                    USER,
                    HOST,
                    DB,
                    COMMAND,
                    TIME,
                    STATE,
                    LEFT(INFO, 100) AS INFO
                FROM information_schema.PROCESSLIST
                WHERE COMMAND != 'Sleep'
                AND DB = DATABASE()
                ORDER BY TIME DESC
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            if results:
                for row in results:
                    print(f"  PID: {row[0]} | User: {row[1]} | Time: {row[5]}s | State: {row[6]}")
                    if row[7]:
                        print(f"       SQL: {row[7]}")
            else:
                print("  ✓ 没有活跃查询")
    
    def generate_optimization_recommendations(self):
        """生成优化建议"""
        self.print_header("10. 优化建议")
        
        recommendations = []
        
        # 检查碎片
        if self.results.get('fragmentation'):
            for table, info in self.results['fragmentation'].items():
                if info.get('needs_optimize'):
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': '表优化',
                        'issue': f'{table} 表碎片率 {info["fragmentation_pct"]:.2f}%',
                        'solution': f'OPTIMIZE TABLE {table};'
                    })
        
        # 检查 COUNT 性能
        if self.results.get('count_performance'):
            for test_name, perf in self.results['count_performance'].items():
                if perf['avg_ms'] > 200:
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'COUNT 性能',
                        'issue': f'{test_name} 查询耗时 {perf["avg_ms"]:.2f}ms',
                        'solution': '1. ANALYZE TABLE 更新统计信息\n' +
                                  '                2. 创建合适的索引\n' +
                                  '                3. 使用应用层缓存'
                    })
        
        # 检查 InnoDB 缓冲池
        if self.results.get('mysql_config', {}).get('innodb_buffer_pool_size'):
            buffer_size = self.results['mysql_config']['innodb_buffer_pool_size']
            if isinstance(buffer_size, str) and buffer_size.isdigit():
                buffer_mb = int(buffer_size) / 1024 / 1024
                if buffer_mb < 128:
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'category': '内存配置',
                        'issue': f'InnoDB 缓冲池仅 {buffer_mb:.0f}MB',
                        'solution': '建议设置为系统内存的 50-70%\n' +
                                  '                在 my.cnf 中设置: innodb_buffer_pool_size = 1G'
                    })
        
        # 输出建议
        if recommendations:
            priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            recommendations.sort(key=lambda x: priority_order[x['priority']])
            
            for i, rec in enumerate(recommendations, 1):
                priority_color = '🔴' if rec['priority'] == 'HIGH' else '🟡' if rec['priority'] == 'MEDIUM' else '🟢'
                print(f"\n  {priority_color} 建议 {i} [{rec['priority']}] - {rec['category']}")
                print(f"     问题: {rec['issue']}")
                print(f"     解决方案: {rec['solution']}")
        else:
            print("\n  ✓ 未发现明显性能问题")
        
        self.results['recommendations'] = recommendations


# ============================================
# Django Management Command
# ============================================

class Command(BaseCommand):
    help = 'MySQL 数据库性能诊断工具'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='以 JSON 格式输出结果'
        )
        
        parser.add_argument(
            '--optimize',
            action='store_true',
            help='自动执行优化操作 (ANALYZE TABLE, OPTIMIZE TABLE)'
        )
    
    def handle(self, *args, **options):
        diagnostics = MySQLDiagnostics()
        results = diagnostics.diagnose_all()
        
        # 如果需要优化
        if options.get('optimize'):
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write("  执行优化操作")
            self.stdout.write("=" * 80)
            
            tables = ['tb_primary_schools', 'tb_secondary_schools']
            
            with connection.cursor() as cursor:
                for table in tables:
                    self.stdout.write(f"\n处理表: {table}")
                    
                    # ANALYZE TABLE
                    self.stdout.write(f"  执行 ANALYZE TABLE {table}...")
                    start = time.time()
                    cursor.execute(f"ANALYZE TABLE {table}")
                    elapsed = (time.time() - start) * 1000
                    self.stdout.write(self.style.SUCCESS(f"  ✓ 完成 ({elapsed:.2f}ms)"))
                    
                    # OPTIMIZE TABLE (如果碎片率 > 10%)
                    if results.get('fragmentation', {}).get(table, {}).get('needs_optimize'):
                        self.stdout.write(f"  执行 OPTIMIZE TABLE {table}...")
                        start = time.time()
                        cursor.execute(f"OPTIMIZE TABLE {table}")
                        elapsed = (time.time() - start) * 1000
                        self.stdout.write(self.style.SUCCESS(f"  ✓ 完成 ({elapsed:.2f}ms)"))
            
            self.stdout.write(self.style.SUCCESS("\n✓ 优化完成"))
        
        # JSON 输出
        if options.get('json'):
            print("\n" + json.dumps(results, indent=2, default=str))


# ============================================
# 独立运行脚本
# ============================================

def run_diagnostics():
    """独立运行诊断 (不依赖 Django management command)"""
    diagnostics = MySQLDiagnostics()
    results = diagnostics.diagnose_all()
    return results


if __name__ == '__main__':
    # 如果直接运行此脚本
    import django
    django.setup()
    run_diagnostics()
