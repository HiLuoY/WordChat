import unittest
import json
import requests
import socketio
import time
import logging
from datetime import datetime
from database.db_utils import get_db_connection
from config import DB_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_challenges.log')
    ]
)
logger = logging.getLogger(__name__)

class TestChallenges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """类级别设置，整个测试类只执行一次"""
        logger.info("\n" + "="*50)
        logger.info("开始执行测试类")
        logger.info("="*50 + "\n")

    @classmethod
    def tearDownClass(cls):
        """类级别清理"""
        logger.info("\n" + "="*50)
        logger.info("测试类执行完毕")
        logger.info("="*50 + "\n")

    def setUp(self):
        """每个测试方法前的准备工作"""
        self.test_start_time = datetime.now()
        logger.info(f"\n=== 开始测试: {self._testMethodName} ===")
        logger.info(f"开始时间: {self.test_start_time}")
        
        # HTTP API基础URL
        self.base_url = 'http://localhost:5000'
        
        # WebSocket客户端
        self.sio = socketio.Client(logger=True, engineio_logger=True)
        
        # 准备测试数据
        try:
            self.prepare_test_data()
            logger.info("测试数据准备完成")
        except Exception as e:
            logger.error(f"准备测试数据失败: {str(e)}")
            raise
        
        # 连接WebSocket
        try:
            logger.info("尝试连接WebSocket...")
            self.sio.connect(self.base_url, wait_timeout=10)
            logger.info(f"WebSocket连接状态: {self.sio.connected}")
        except Exception as e:
            logger.error(f"WebSocket连接失败: {str(e)}")
            raise
        
        logger.info("测试初始化完成\n")

    def tearDown(self):
        """每个测试方法后的清理工作"""
        # 断开WebSocket连接
        try:
            if hasattr(self, 'sio') and self.sio.connected:
                self.sio.disconnect()
                logger.info("WebSocket已断开连接")
        except Exception as e:
            logger.error(f"断开WebSocket连接时出错: {str(e)}")
        
        # 清理测试数据
        try:
            self.cleanup_test_data()
            logger.info("测试数据清理完成")
        except Exception as e:
            logger.error(f"清理测试数据时出错: {str(e)}")
        
        test_duration = datetime.now() - self.test_start_time
        logger.info(f"测试 {self._testMethodName} 耗时: {test_duration.total_seconds():.2f}秒")
        logger.info(f"=== 结束测试: {self._testMethodName} ===\n")

    def prepare_test_data(self):
        """准备测试数据"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            logger.debug("数据库连接成功")
            
            # 检查并删除可能存在的测试数据
            logger.debug("清理可能存在的旧测试数据...")
            cursor.execute("DELETE FROM challenge_attempts WHERE challenge_id IN (SELECT id FROM word_challenges WHERE room_id = 1)")
            cursor.execute("DELETE FROM word_challenges WHERE room_id = 1")
            cursor.execute("DELETE FROM rooms WHERE id = 1")
            cursor.execute("DELETE FROM words WHERE id = 1")
            
            # 插入测试数据
            logger.debug("插入新的测试数据...")
            cursor.execute("INSERT INTO rooms (id, name) VALUES (1, '测试房间')")
            cursor.execute("""
                INSERT INTO words (id, word, meaning, hint) 
                VALUES (1, 'test', '测试', '这是一个测试单词')
            """)
            conn.commit()
            logger.info("测试数据准备完成")
        except Exception as e:
            logger.error(f"准备测试数据时出错: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def cleanup_test_data(self):
        """清理测试数据"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            logger.debug("清理测试数据...")
            
            # 清理测试数据
            cursor.execute("DELETE FROM challenge_attempts WHERE challenge_id IN (SELECT id FROM word_challenges WHERE room_id = 1)")
            cursor.execute("DELETE FROM word_challenges WHERE room_id = 1")
            cursor.execute("DELETE FROM rooms WHERE id = 1")
            cursor.execute("DELETE FROM words WHERE id = 1")
            
            conn.commit()
            logger.info("测试数据清理完成")
        except Exception as e:
            logger.error(f"清理测试数据时出错: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def test_create_challenge(self):
        """测试创建挑战"""
        try:
            logger.info("测试创建挑战...")
            url = f'{self.base_url}/challenges/create'
            data = {
                'room_id': 1,
                'word_id': 1,
                'round_number': 1
            }
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求数据: {json.dumps(data, indent=2)}")
            
            response = requests.post(url, json=data)
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            self.assertEqual(response.status_code, 201, 
                           f"预期状态码201，实际得到{response.status_code}。响应内容: {response.text}")
            
            response_data = response.json()
            self.assertEqual(response_data['code'], 201, 
                           f"预期返回码201，实际得到{response_data.get('code')}")
            
            self.challenge_id = response_data['data']['challenge_id']
            logger.info(f"创建挑战成功，挑战ID: {self.challenge_id}")
        except Exception as e:
            logger.error(f"测试失败: {str(e)}")
            raise

    def test_get_challenge(self):
        """测试获取挑战详情"""
        try:
            logger.info("测试获取挑战...")
            
            # 先创建一个挑战
            self.test_create_challenge()
            
            url = f'{self.base_url}/challenges/{self.challenge_id}'
            logger.debug(f"请求URL: {url}")
            
            response = requests.get(url)
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertEqual(response_data['code'], 200)
            self.assertEqual(response_data['data']['room_id'], 1)
            self.assertEqual(response_data['data']['word_id'], 1)
            
            logger.info("获取挑战测试通过")
        except Exception as e:
            logger.error(f"测试失败: {str(e)}")
            raise

    def test_get_current_challenge(self):
        """测试获取当前挑战"""
        try:
            logger.info("测试获取当前挑战...")
            
            # 先创建一个挑战
            self.test_create_challenge()
            
            url = f'{self.base_url}/challenges/current/1'
            logger.debug(f"请求URL: {url}")
            
            response = requests.get(url)
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertEqual(response_data['code'], 200)
            self.assertEqual(response_data['data']['room_id'], 1)
            
            logger.info("获取当前挑战测试通过")
        except Exception as e:
            logger.error(f"测试失败: {str(e)}")
            raise

    def test_websocket_answer(self):
        """测试WebSocket答案提交"""
        try:
            logger.info("测试WebSocket答案提交...")
            
            # 先创建一个挑战
            self.test_create_challenge()
            
            # 用于存储WebSocket响应
            self.ws_response = None
            
            @self.sio.on('answer_result')
            def on_answer_result(data):
                logger.debug(f"收到WebSocket消息: {json.dumps(data, indent=2)}")
                self.ws_response = data
            
            # 提交答案
            answer_data = {
                'room_id': 1,
                'challenge_id': self.challenge_id,
                'answer': 'test',
                'user_id': 1
            }
            logger.debug(f"发送WebSocket消息: {json.dumps(answer_data, indent=2)}")
            self.sio.emit('submit_answer', answer_data)
            
            # 等待响应
            wait_time = 0
            while wait_time < 5 and self.ws_response is None:
                time.sleep(0.5)
                wait_time += 0.5
                logger.debug(f"等待WebSocket响应... {wait_time}秒")
            
            # 验证响应
            self.assertIsNotNone(self.ws_response, "未收到WebSocket响应")
            self.assertTrue(self.ws_response['correct'], "答案应为正确")
            self.assertEqual(self.ws_response['word'], 'test', "返回的单词不匹配")
            
            logger.info("WebSocket答案提交测试通过")
        except Exception as e:
            logger.error(f"测试失败: {str(e)}")
            raise
        finally:
            # 移除事件处理器
            if hasattr(self, 'sio'):
                self.sio.off('answer_result')

    def test_websocket_room_events(self):
        """测试WebSocket房间事件"""
        try:
            logger.info("测试WebSocket房间事件...")
            
            # 用于存储WebSocket响应
            self.ws_messages = []
            
            @self.sio.on('status')
            def on_status(data):
                logger.debug(f"收到WebSocket状态消息: {json.dumps(data, indent=2)}")
                self.ws_messages.append(data)
            
            # 加入房间
            join_data = {'room_id': 1}
            logger.debug(f"发送加入房间消息: {json.dumps(join_data, indent=2)}")
            self.sio.emit('join', join_data)
            time.sleep(1)
            
            # 离开房间
            leave_data = {'room_id': 1}
            logger.debug(f"发送离开房间消息: {json.dumps(leave_data, indent=2)}")
            self.sio.emit('leave', leave_data)
            time.sleep(1)
            
            # 验证消息
            self.assertGreaterEqual(len(self.ws_messages), 2, "应至少收到2条状态消息")
            self.assertIn('用户加入房间', self.ws_messages[0]['msg'], "第一条消息应为加入通知")
            self.assertIn('用户离开房间', self.ws_messages[1]['msg'], "第二条消息应为离开通知")
            
            logger.info("WebSocket房间事件测试通过")
        except Exception as e:
            logger.error(f"测试失败: {str(e)}")
            raise
        finally:
            # 移除事件处理器
            if hasattr(self, 'sio'):
                self.sio.off('status')

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)