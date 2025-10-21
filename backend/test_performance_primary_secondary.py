#!/usr/bin/env python3
"""
小学和中学接口性能测试脚本
测试优化后的API接口响应时间和吞吐量
"""
import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


class PerformanceTester:
    """API性能测试器"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_single_request(self, endpoint, params=None):
        """测试单个请求"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            duration = time.time() - start_time
            
            return {
                'success': response.status_code == 200,
                'duration': duration,
                'status_code': response.status_code,
                'cache_hit': response.headers.get('X-Cache-Hit', 'N/A'),
                'db_queries': response.headers.get('X-Database-Queries', 'N/A'),
                'db_time': response.headers.get('X-Database-Time', 'N/A')
            }
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    def test_multiple_requests(self, endpoint, params=None, count=10):
        """测试多次请求（串行）"""
        results = []
        
        print(f"\n测试 {count} 次请求: {endpoint}")
        print("=" * 60)
        
        for i in range(count):
            result = self.test_single_request(endpoint, params)
            results.append(result)
            
            status = "✓" if result['success'] else "✗"
            cache = result.get('cache_hit', 'N/A')
            duration = result['duration']
            
            # 高亮慢请求
            if duration > 0.5:
                status = "⚠️ " + status
            
            print(f"{status} 请求 #{i+1}: {duration:.3f}s (缓存: {cache})")
        
        return results
    
    def test_concurrent_requests(self, endpoint, params=None, concurrent=10, total=50):
        """测试并发请求"""
        results = []
        
        print(f"\n并发测试: {concurrent} 并发, 共 {total} 请求")
        print("=" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent) as executor:
            futures = [
                executor.submit(self.test_single_request, endpoint, params)
                for _ in range(total)
            ]
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                completed += 1
                
                if completed % 10 == 0:
                    print(f"已完成: {completed}/{total}")
        
        total_time = time.time() - start_time
        print(f"总耗时: {total_time:.2f}s")
        
        return results
    
    def print_statistics(self, results):
        """打印统计信息"""
        if not results:
            print("没有测试结果")
            return
        
        # 过滤成功的请求
        successful = [r for r in results if r.get('success')]
        failed = len(results) - len(successful)
        
        if not successful:
            print(f"\n所有请求都失败了！失败数: {failed}")
            return
        
        durations = [r['duration'] for r in successful]
        
        print(f"\n{'=' * 60}")
        print("统计结果")
        print(f"{'=' * 60}")
        print(f"总请求数:     {len(results)}")
        print(f"成功数:       {len(successful)}")
        print(f"失败数:       {failed}")
        print(f"成功率:       {len(successful)/len(results)*100:.1f}%")
        print(f"\n响应时间:")
        print(f"  最小值:     {min(durations):.3f}s")
        print(f"  最大值:     {max(durations):.3f}s")
        print(f"  平均值:     {statistics.mean(durations):.3f}s")
        print(f"  中位数:     {statistics.median(durations):.3f}s")
        
        if len(durations) > 1:
            print(f"  标准差:     {statistics.stdev(durations):.3f}s")
        
        # 性能评级
        avg_time = statistics.mean(durations)
        if avg_time < 0.1:
            rating = "🚀 优秀"
        elif avg_time < 0.3:
            rating = "⚡ 良好"
        elif avg_time < 0.5:
            rating = "✓ 一般"
        else:
            rating = "⚠️ 需要优化"
        
        print(f"\n性能评级:     {rating}")
        
        # 计算吞吐量
        total_time = sum(durations)
        if total_time > 0:
            throughput = len(successful) / total_time
            print(f"吞吐量:       {throughput:.2f} req/s")
        
        # 缓存命中率
        cache_hits = sum(1 for r in successful if r.get('cache_hit') == 'HIT')
        if cache_hits > 0:
            print(f"缓存命中率:   {cache_hits/len(successful)*100:.1f}%")


def main():
    """主函数"""
    # 配置
    BASE_URL = "http://9.135.78.24/api/schools"
    
    tester = PerformanceTester(BASE_URL)
    
    print("=" * 60)
    print("小学和中学接口性能测试")
    print("=" * 60)
    print(f"基础URL: {BASE_URL}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ========================================
    # 小学接口测试
    # ========================================
    print("\n\n" + "=" * 60)
    print("📚 小学接口测试")
    print("=" * 60)
    
    # 测试1: 小学列表（基础查询）
    print("\n\n[测试1] 小学列表接口 - 基础查询")
    results1 = tester.test_multiple_requests(
        "/primary/",
        params={'page': 1, 'pageSize': 20},
        count=10
    )
    tester.print_statistics(results1)
    
    # 测试2: 小学列表（带地区筛选）
    print("\n\n[测试2] 小学列表接口 - 地区筛选")
    results2 = tester.test_multiple_requests(
        "/primary/",
        params={'district': '中西区', 'page': 1, 'pageSize': 20},
        count=10
    )
    tester.print_statistics(results2)
    
    # 测试3: 小学列表（搜索）
    print("\n\n[测试3] 小学列表接口 - 关键词搜索")
    results3 = tester.test_multiple_requests(
        "/primary/",
        params={'keyword': '圣', 'page': 1, 'pageSize': 20},
        count=10
    )
    tester.print_statistics(results3)
    
    # 测试4: 小学统计接口
    print("\n\n[测试4] 小学统计接口")
    results4 = tester.test_multiple_requests(
        "/primary/stats/",
        count=10
    )
    tester.print_statistics(results4)
    
    # 测试5: 小学筛选器接口
    print("\n\n[测试5] 小学筛选器接口")
    results5 = tester.test_multiple_requests(
        "/primary/filters/",
        count=10
    )
    tester.print_statistics(results5)
    
    # 测试6: 小学并发测试
    print("\n\n[测试6] 小学列表 - 并发测试")
    results6 = tester.test_concurrent_requests(
        "/primary/",
        params={'page': 1, 'pageSize': 20},
        concurrent=10,
        total=50
    )
    tester.print_statistics(results6)
    
    # ========================================
    # 中学接口测试
    # ========================================
    print("\n\n" + "=" * 60)
    print("🎓 中学接口测试")
    print("=" * 60)
    
    # 测试7: 中学列表（基础查询）
    print("\n\n[测试7] 中学列表接口 - 基础查询")
    results7 = tester.test_multiple_requests(
        "/secondary/",
        params={'page': 1, 'pageSize': 20},
        count=10
    )
    tester.print_statistics(results7)
    
    # 测试8: 中学列表（带地区筛选）
    print("\n\n[测试8] 中学列表接口 - 地区筛选")
    results8 = tester.test_multiple_requests(
        "/secondary/",
        params={'district': '中西区', 'page': 1, 'pageSize': 20},
        count=10
    )
    tester.print_statistics(results8)
    
    # 测试9: 中学列表（搜索）
    print("\n\n[测试9] 中学列表接口 - 关键词搜索")
    results9 = tester.test_multiple_requests(
        "/secondary/",
        params={'keyword': '圣', 'page': 1, 'pageSize': 20},
        count=10
    )
    tester.print_statistics(results9)
    
    # 测试10: 中学统计接口
    print("\n\n[测试10] 中学统计接口")
    results10 = tester.test_multiple_requests(
        "/secondary/stats/",
        count=10
    )
    tester.print_statistics(results10)
    
    # 测试11: 中学并发测试
    print("\n\n[测试11] 中学列表 - 并发测试")
    results11 = tester.test_concurrent_requests(
        "/secondary/",
        params={'page': 1, 'pageSize': 20},
        concurrent=10,
        total=50
    )
    tester.print_statistics(results11)
    
    # ========================================
    # 总结报告
    # ========================================
    print("\n\n" + "=" * 60)
    print("📊 测试总结报告")
    print("=" * 60)
    
    all_results = results1 + results2 + results3 + results4 + results5 + results6 + \
                  results7 + results8 + results9 + results10 + results11
    
    successful = [r for r in all_results if r.get('success')]
    
    if successful:
        avg_time = statistics.mean([r['duration'] for r in successful])
        cache_hits = sum(1 for r in successful if r.get('cache_hit') == 'HIT')
        
        print(f"\n总测试数:     {len(all_results)}")
        print(f"成功数:       {len(successful)}")
        print(f"失败数:       {len(all_results) - len(successful)}")
        print(f"平均响应时间: {avg_time:.3f}s")
        print(f"缓存命中率:   {cache_hits/len(successful)*100:.1f}%")
        
        # 性能改善建议
        if avg_time > 0.5:
            print("\n⚠️ 建议:")
            print("  - 检查数据库索引是否已创建")
            print("  - 确认Redis缓存是否正常工作")
            print("  - 查看慢查询日志")
        elif avg_time > 0.3:
            print("\n✓ 性能良好，可以考虑:")
            print("  - 进一步优化查询逻辑")
            print("  - 增加缓存时间")
        else:
            print("\n🚀 性能优秀！")
    
    print("\n\n测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n\n测试出错: {e}")
        import traceback
        traceback.print_exc()

