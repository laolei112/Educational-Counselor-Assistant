#!/usr/bin/env python3
"""
性能测试脚本
测试API接口的响应时间和吞吐量
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
            print(f"{status} 请求 #{i+1}: {result['duration']:.3f}s (缓存: {cache})")
        
        return results
    
    def test_concurrent_requests(self, endpoint, params=None, concurrent=10, total=100):
        """测试并发请求"""
        results = []
        
        print(f"\n并发测试: {concurrent} 并发, 共 {total} 请求")
        print("=" * 60)
        
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
        
        # 计算吞吐量
        total_time = sum(durations)
        if total_time > 0:
            throughput = len(successful) / total_time
            print(f"\n吞吐量:       {throughput:.2f} req/s")
        
        # 缓存命中率
        cache_hits = sum(1 for r in successful if r.get('cache_hit') == 'HIT')
        if cache_hits > 0:
            print(f"\n缓存命中率:   {cache_hits/len(successful)*100:.1f}%")


def main():
    """主函数"""
    # 配置
    BASE_URL = "http://9.135.78.24/api"
    
    tester = PerformanceTester(BASE_URL)
    
    print("=" * 60)
    print("API 性能测试")
    print("=" * 60)
    
    # 测试1: 学校列表接口（小学）
    print("\n\n[测试1] 学校列表接口 - 小学")
    results1 = tester.test_multiple_requests(
        "/schools/",
        params={'type': 'primary', 'page': 1, 'pageSize': 20},
        count=10
    )
    tester.print_statistics(results1)
    
    # 测试2: 学校列表接口（中学）
    print("\n\n[测试2] 学校列表接口 - 中学")
    results2 = tester.test_multiple_requests(
        "/schools/",
        params={'type': 'secondary', 'page': 1, 'pageSize': 20},
        count=10
    )
    tester.print_statistics(results2)
    
    # 测试3: 统计接口
    print("\n\n[测试3] 统计接口")
    results3 = tester.test_multiple_requests(
        "/schools/stats/",
        params={'type': 'primary'},
        count=10
    )
    tester.print_statistics(results3)
    
    # 测试4: 并发测试
    print("\n\n[测试4] 并发测试")
    results4 = tester.test_concurrent_requests(
        "/schools/",
        params={'type': 'primary', 'page': 1, 'pageSize': 20},
        concurrent=10,
        total=50
    )
    tester.print_statistics(results4)
    
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

