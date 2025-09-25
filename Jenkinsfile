pipeline {
    agent any  // 使用任意可用节点

    stages {
        stage('Checkout') {
            steps {
                checkout scm  // 拉取 GitHub 代码
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 --version'  // 检查 Python 环境
                sh 'pip3 install dotenv'
                sh 'pip3 install colorama'
                sh 'pip3 install netmiko'
                // 可选：安装依赖（如 pip install -r requirements.txt）
            }
        }

        stage('Run Python Script') {
            steps {
                // 使用 withCredentials 指令将凭证注入到环境变量
                withCredentials([
                    // 绑定用户名密码凭证到两个环境变量：MY_USERNAME 和 MY_PASSWORD
                    usernamePassword(
                        credentialsId: 'CISCO-ID',
                        usernameVariable: 'CISCO_USERNAME', // 自定义用户名环境变量名
                        passwordVariable: 'CISCO_PASSWORD'  // 自定义密码环境变量名
                    ),
                    usernamePassword(
                        credentialsId: 'FTP-ID',
                        usernameVariable: 'FTP_USERNAME', // 自定义用户名环境变量名
                        passwordVariable: 'FTP_PASSWORD'  // 自定义密码环境变量名
                    ),
                    string(
                        credentialsId: 'Jenkins_webhook',
                        variable: 'TEAMS_WEBHOOK' // 自定义密钥环境变量名
                    )
                ]) {
                    // 在这个块内的所有步骤都可以访问到上面定义的环境变量
                    echo "Username is $CISCO_USERNAME"
                    echo "Password is $CISCO_PASSWORD" // Jenkins 会自动用 **** 屏蔽值
                   
                    // 执行你的 Python 脚本
                    sh 'python3 get_WLC_log_AP_DOWN.py'  // 运行 Python 文件
                }   
            }
        }
    }
}
