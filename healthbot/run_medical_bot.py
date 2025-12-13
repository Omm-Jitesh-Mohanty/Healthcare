import subprocess
import threading
import time
import webbrowser

def run_medical_bot():
    """Run the medical bot with action server"""
    
    def run_actions():
        print("🔧 Starting Medical Action Server...")
        print("   Server will run on: http://localhost:5055")
        subprocess.run(['rasa', 'run', 'actions', '--port', '5055'])
    
    def run_rasa_shell():
        time.sleep(5)  # Wait for action server to start
        print("\n💬 Starting Medical Bot Chat Interface...")
        print("   You can now chat with your medical assistant!")
        print("   Type 'quit' to exit\n")
        subprocess.run(['rasa', 'shell'])
    
    print("🏥 Starting Comprehensive Medical Bot...")
    print("=" * 50)
    
    # Start action server in separate thread
    actions_thread = threading.Thread(target=run_actions)
    actions_thread.daemon = True
    actions_thread.start()
    
    # Start rasa shell
    run_rasa_shell()

if __name__ == "__main__":
    run_medical_bot()