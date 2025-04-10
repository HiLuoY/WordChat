import unittest
import requests
import socketio
import time
import json
import pymysql
import logging
from werkzeug.security import generate_password_hash
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestWordChallenge(unittest.TestCase):
    """单词挑战功能测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化，创建测试用户和单词"""
        try:
            # 数据库配置
            db_config = {
                'host': 'localhost',
                'user': 'root',
                'password': 'test',  # 使用与db_utils.py相同的密码
                'database': 'elp',
                'cursorclass': pymysql.cursors.DictCursor
            }
            
            logger.info("正在连接数据库...")
            # 连接数据库
            conn = pymysql.connect(**db_config)
            
            try:
                with conn.cursor() as cursor:
                    # 检查测试用户是否存在
                    logger.info("检查测试用户...")
                    cursor.execute("SELECT id FROM Users WHERE email = %s", ('test@example.com',))
                    user = cursor.fetchone()
                    
                    if not user:
                        # 创建测试用户
                        logger.info("创建测试用户...")
                        password_hash = generate_password_hash('test123')
                        cursor.execute(
                            "INSERT INTO Users (email, password_hash, nickname) VALUES (%s, %s, %s)",
                            ('test@example.com', password_hash, 'Test User')
                        )
                        conn.commit()
                        logger.info("✅ 创建测试用户成功")
                    else:
                        logger.info("✅ 测试用户已存在")
                    
                    # 检查测试单词是否存在
                    logger.info("检查测试单词...")
                    cursor.execute("SELECT id FROM Words WHERE word = %s", ('test',))
                    word = cursor.fetchone()
                    
                    if not word:
                        # 创建测试单词
                        logger.info("创建测试单词...")
                        cursor.execute(
                            "INSERT INTO Words (word, meaning) VALUES (%s, %s)",
                            ('test', '测试')
                        )
                        conn.commit()
                        logger.info("✅ 创建测试单词成功")
                    else:
                        logger.info("✅ 测试单词已存在")
                        
                    # 获取测试单词ID
                    logger.info("获取测试单词ID...")
                    cursor.execute("SELECT id FROM Words WHERE word = %s", ('test',))
                    result = cursor.fetchone()
                    if not result:
                        raise Exception("无法获取测试单词ID")
                    cls.test_word_id = result['id']
                    logger.info(f"✅ 测试单词ID: {cls.test_word_id}")
                    
            except pymysql.Error as e:
                logger.error(f"❌ 数据库操作失败: {str(e)}")
                raise
            finally:
                conn.close()
                logger.info("数据库连接已关闭")
                
        except Exception as e:
            logger.error(f"❌ 初始化失败: {str(e)}")
            raise
    
    def setUp(self):
        """测试前准备"""
        try:
            self.base_url = 'http://localhost:5000'
            self.test_user_id = 1  # 使用已有的测试用户ID
            self.test_room_id = None
            self.test_challenge_id = None
            
            # 创建会话对象并配置重试机制
            self.session = requests.Session()
            retry_strategy = Retry(
                total=3,  # 最多重试3次
                backoff_factor=1,  # 重试间隔
                status_forcelist=[500, 502, 503, 504, 404, 429],  # 需要重试的HTTP状态码
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            
            # 先进行登录
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    logger.info("正在登录...")
                    login_response = self.session.post(
                        f'{self.base_url}/login',
                        json={
                            'email': 'test@example.com',  # 使用测试账号
                            'password': 'test123'
                        },
                        timeout=10  # 设置超时时间
                    )
                    if login_response.status_code == 200:
                        logger.info("✅ 登录成功")
                        break
                    else:
                        logger.error(f"❌ 登录失败: {login_response.json()}")
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(1)  # 等待1秒后重试
                        else:
                            raise Exception("登录失败，请确保测试账号存在且密码正确")
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    logger.warning(f"登录连接错误，正在重试 ({retry_count + 1}/{max_retries}): {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(1)
                    else:
                        raise Exception(f"登录失败，连接错误: {str(e)}")
            
            # 创建测试房间
            logger.info("正在创建测试房间...")
            response = self.session.post(
                f'{self.base_url}/rooms',
                json={
                    'room_name': f'测试单词挑战房间_{int(time.time())}',  # 使用时间戳确保房间名唯一
                    'password': None
                },
                timeout=10
            )
            if response.status_code != 201:
                logger.error(f"❌ 创建房间失败: {response.json()}")
                raise Exception(f"创建房间失败，状态码: {response.status_code}")
                
            self.test_room_id = response.json()['room_id']
            logger.info(f"✅ 成功创建测试房间，ID: {self.test_room_id}")
            
            # 初始化WebSocket客户端
            logger.info("正在连接WebSocket...")
            self.sio = socketio.Client()
            try:
                # 获取会话cookie
                cookies = self.session.cookies.get_dict()
                # 将cookie添加到WebSocket连接中
                self.sio.connect(
                    'http://localhost:5000',
                    headers={'Cookie': '; '.join([f'{k}={v}' for k, v in cookies.items()])},
                    wait_timeout=10
                )
                logger.info("✅ WebSocket连接成功")
            except Exception as e:
                logger.error(f"❌ WebSocket连接失败: {str(e)}")
                raise
                
        except Exception as e:
            logger.error(f"❌ 测试准备失败: {str(e)}")
            raise
        
    def tearDown(self):
        """测试后清理"""
        try:
            # 断开WebSocket连接
            if hasattr(self, 'sio') and self.sio.connected:
                try:
                    self.sio.disconnect()
                    logger.info("WebSocket连接已断开")
                except Exception as e:
                    logger.warning(f"断开WebSocket连接时出错: {str(e)}")
                
            # 删除测试房间（如果有相关API）
            if self.test_room_id:
                try:
                    response = self.session.post(
                        f'{self.base_url}/rooms/{self.test_room_id}/leave',
                        timeout=10
                    )
                    if response.status_code == 200:
                        logger.info(f"✅ 成功离开测试房间 {self.test_room_id}")
                    else:
                        logger.error(f"❌ 离开房间失败: {response.json()}")
                except Exception as e:
                    logger.error(f"❌ 清理测试房间时出错: {str(e)}")
        except Exception as e:
            logger.error(f"❌ 测试清理失败: {str(e)}")
    
    def test_create_challenge(self):
        """测试创建单词挑战"""
        try:
            logger.info("\n开始测试创建单词挑战...")
            response = self.session.post(
                f'{self.base_url}/challenges/create',
                json={
                    'room_id': self.test_room_id,
                    'word_id': self.test_word_id,  # 使用测试单词ID
                    'time_limit': 60
                },
                timeout=10
            )
            logger.info(f"创建挑战响应: {response.json()}")
            self.assertEqual(response.status_code, 201, f"创建挑战失败，状态码: {response.status_code}")
            response_data = response.json()
            self.assertIn('data', response_data, "响应中缺少data字段")
            self.assertIn('challenge_id', response_data['data'], "响应中缺少challenge_id字段")
            self.test_challenge_id = response_data['data']['challenge_id']
            logger.info(f"✅ 成功创建挑战，ID: {self.test_challenge_id}")
        except Exception as e:
            logger.error(f"❌ 创建挑战测试失败: {str(e)}")
            raise
        
    def test_get_challenge(self):
        """测试获取单词挑战"""
        try:
            logger.info("\n开始测试获取单词挑战...")
            # 先创建一个挑战
            self.test_create_challenge()
            
            # 获取挑战详情
            response = self.session.get(
                f'{self.base_url}/challenges/{self.test_challenge_id}',
                timeout=10
            )
            logger.info(f"获取挑战响应: {response.json()}")
            self.assertEqual(response.status_code, 200, f"获取挑战失败，状态码: {response.status_code}")
            response_data = response.json()
            self.assertIn('data', response_data, "响应中缺少data字段")
            challenge_data = response_data['data']
            self.assertEqual(challenge_data['id'], self.test_challenge_id, "挑战ID不匹配")
            self.assertEqual(challenge_data['room_id'], self.test_room_id, "房间ID不匹配")
            self.assertEqual(challenge_data['word_id'], self.test_word_id, "单词ID不匹配")
            self.assertEqual(challenge_data['status'], 'ongoing', "挑战状态不正确")
            logger.info("✅ 成功获取挑战详情")
        except Exception as e:
            logger.error(f"❌ 获取挑战测试失败: {str(e)}")
            raise
        
    def test_submit_answer(self):
        """测试提交答案"""
        try:
            logger.info("\n开始测试提交答案...")
            # 先创建一个挑战
            self.test_create_challenge()
            
            # 准备WebSocket事件监听
            answer_result = None
            
            @self.sio.on('answer_result')
            def on_answer_result(data):
                nonlocal answer_result
                answer_result = data
                logger.info(f"收到答案结果: {data}")
                
            # 加入房间
            logger.info("正在加入房间...")
            self.sio.emit('join_room', {'room_id': self.test_room_id})
            time.sleep(1)  # 等待加入房间
            
            # 提交答案
            logger.info("正在提交答案...")
            self.sio.emit('submit_answer', {
                'room_id': self.test_room_id,
                'challenge_id': self.test_challenge_id,
                'answer': 'test',  # 使用正确的测试单词
                'user_id': self.test_user_id
            })
            
            # 等待结果
            time.sleep(2)
            self.assertIsNotNone(answer_result, "未收到答案结果")
            self.assertIn('correct', answer_result, "答案结果中缺少correct字段")
            self.assertIn('message', answer_result, "答案结果中缺少message字段")
            logger.info("✅ 答案提交测试完成")
        except Exception as e:
            logger.error(f"❌ 提交答案测试失败: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main() 