import requests
import json
import logging
from database.db_utils import get_db_connection
from models.wordchallenge_models import WordChallenge

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = 'http://localhost:5000'

def setup_test_data():
    """准备测试数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查并创建测试房间
        cursor.execute("SELECT id FROM rooms WHERE id = 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO rooms (id, name) VALUES (1, '测试房间')")
            
        # 检查并创建测试单词
        cursor.execute("SELECT id FROM words WHERE id = 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO words (id, word, meaning) VALUES (1, 'test', '测试')")
            
        conn.commit()
        logger.info("测试数据准备完成")
    except Exception as e:
        logger.error(f"准备测试数据失败: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def test_create_challenge():
    """测试创建挑战"""
    url = f'{BASE_URL}/challenges/create'
    data = {
        'room_id': 1,
        'word_id': 1,
        'round_number': 1
    }
    
    try:
        response = requests.post(url, json=data)
        logger.info(f"创建挑战响应: {response.json()}")
        assert response.status_code == 201
        assert response.json()['code'] == 201
        return response.json()['data']['challenge_id']
    except AssertionError as e:
        logger.error(f"创建挑战测试失败: {str(e)}")
        raise

def test_get_challenge(challenge_id):
    """测试获取挑战详情"""
    url = f'{BASE_URL}/challenges/{challenge_id}'
    
    try:
        response = requests.get(url)
        logger.info(f"获取挑战详情响应: {response.json()}")
        assert response.status_code == 200
        assert response.json()['code'] == 200
    except AssertionError as e:
        logger.error(f"获取挑战详情测试失败: {str(e)}")
        raise

def test_get_current_challenge():
    """测试获取当前挑战"""
    url = f'{BASE_URL}/challenges/current/1'
    
    try:
        response = requests.get(url)
        logger.info(f"获取当前挑战响应: {response.json()}")
        assert response.status_code in [200, 404]
    except AssertionError as e:
        logger.error(f"获取当前挑战测试失败: {str(e)}")
        raise

def test_get_challenge_history():
    """测试获取挑战历史"""
    url = f'{BASE_URL}/challenges/history/1'
    
    try:
        response = requests.get(url)
        logger.info(f"获取挑战历史响应: {response.json()}")
        assert response.status_code == 200
        assert response.json()['code'] == 200
    except AssertionError as e:
        logger.error(f"获取挑战历史测试失败: {str(e)}")
        raise

def test_update_challenge_status(challenge_id):
    """测试更新挑战状态"""
    url = f'{BASE_URL}/challenges/{challenge_id}/status'
    data = {'status': 'in_progress'}
    
    try:
        response = requests.put(url, json=data)
        logger.info(f"更新挑战状态响应: {response.json()}")
        assert response.status_code == 200
        assert response.json()['code'] == 200
    except AssertionError as e:
        logger.error(f"更新挑战状态测试失败: {str(e)}")
        raise

def test_increment_round(challenge_id):
    """测试增加轮次"""
    url = f'{BASE_URL}/challenges/{challenge_id}/round'
    
    try:
        response = requests.put(url)
        logger.info(f"增加轮次响应: {response.json()}")
        assert response.status_code == 200
        assert response.json()['code'] == 200
    except AssertionError as e:
        logger.error(f"增加轮次测试失败: {str(e)}")
        raise

def test_finish_challenge(challenge_id):
    """测试结束挑战"""
    url = f'{BASE_URL}/challenges/{challenge_id}/finish'
    
    try:
        response = requests.put(url)
        logger.info(f"结束挑战响应: {response.json()}")
        assert response.status_code == 200
        assert response.json()['code'] == 200
    except AssertionError as e:
        logger.error(f"结束挑战测试失败: {str(e)}")
        raise

def test_get_challenge_word(challenge_id):
    """测试获取挑战单词"""
    url = f'{BASE_URL}/challenges/{challenge_id}/word'
    
    try:
        response = requests.get(url)
        logger.info(f"获取挑战单词响应: {response.json()}")
        assert response.status_code == 200
        assert response.json()['code'] == 200
    except AssertionError as e:
        logger.error(f"获取挑战单词测试失败: {str(e)}")
        raise

def cleanup_test_data():
    """清理测试数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 清理测试数据
        cursor.execute("DELETE FROM word_challenges WHERE room_id = 1")
        cursor.execute("DELETE FROM rooms WHERE id = 1")
        cursor.execute("DELETE FROM words WHERE id = 1")
        
        conn.commit()
        logger.info("测试数据清理完成")
    except Exception as e:
        logger.error(f"清理测试数据失败: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def run_all_tests():
    """运行所有测试"""
    try:
        logger.info("开始运行API测试...")
        
        # 准备测试数据
        setup_test_data()
        
        # 创建挑战并获取challenge_id
        challenge_id = test_create_challenge()
        
        # 运行其他测试
        test_get_challenge(challenge_id)
        test_get_current_challenge()
        test_get_challenge_history()
        test_update_challenge_status(challenge_id)
        test_increment_round(challenge_id)
        test_get_challenge_word(challenge_id)
        test_finish_challenge(challenge_id)
        
        logger.info("所有测试完成！")
        
        # 清理测试数据
        cleanup_test_data()
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        raise

if __name__ == '__main__':
    run_all_tests() 