import time
import requests
import concurrent.futures
import random
import uuid

API_URL = "http://localhost:8000/api/v1"

def simulate_user_flow(user_id):
    """Simulate a complete user interaction flow"""
    session = requests.Session()
    session_id = None
    
    try:
        # 1. Start Conversation
        start_payload = {
            "user_info": {"age": random.randint(18, 80), "gender": random.choice(["male", "female"])},
            "location": {"city": "New York", "country": "USA"}
        }
        res = session.post(f"{API_URL}/chatbot/start", json=start_payload)
        if res.status_code == 200:
            session_id = res.json().get("session_id")
        else:
            return False, f"Start failed: {res.status_code}"
            
        # 2. Send Message (Symptom)
        symptoms = ["headache", "fever", "cough", "chest pain", "stomach ache"]
        msg_payload = {
            "session_id": session_id,
            "message": f"I have {random.choice(symptoms)}"
        }
        res = session.post(f"{API_URL}/chatbot/message", json=msg_payload)
        if res.status_code != 200:
            return False, f"Message 1 failed: {res.status_code}"
            
        # 3. Send Message (Follow-up)
        msg_payload["message"] = "It started yesterday"
        res = session.post(f"{API_URL}/chatbot/message", json=msg_payload)
        
        # 4. End Conversation
        end_payload = {"session_id": session_id}
        res = session.post(f"{API_URL}/chatbot/end", json=end_payload)
        
        return True, "Success"
        
    except Exception as e:
        return False, str(e)

def run_load_test(total_users=50, concurrent_users=10):
    print(f"Starting Load Test: {total_users} users with {concurrent_users} concurrency")
    
    start_time = time.time()
    success_count = 0
    fail_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(simulate_user_flow, i) for i in range(total_users)]
        
        for future in concurrent.futures.as_completed(futures):
            success, message = future.result()
            if success:
                success_count += 1
            else:
                fail_count += 1
                # print(f"Failure: {message}")
                
    duration = time.time() - start_time
    
    print("\nLoad Test Results:")
    print(f"Total Requests: {total_users * 4} (approx)")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Throughput: {total_users / duration:.2f} users/sec")
    print(f"Success Rate: {(success_count/total_users)*100:.1f}%")
    print(f"Failures: {fail_count}")

if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(f"{API_URL.replace('/api/v1', '')}/health")
        run_load_test()
    except:
        print("Backend not running at http://localhost:8000. Please start it first.")
