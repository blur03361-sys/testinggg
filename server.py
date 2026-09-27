from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import base64

def encode_varint(val):
    buf = bytearray()
    while val >= 0x80:
        buf.append((val & 0x7F) | 0x80)
        val >>= 7
    buf.append(val & 0x7F)
    return bytes(buf)

def encode_pb_string(field_num, s):
    if not s:
        return b""
    tag = (field_num << 3) | 2
    b_s = s.encode('utf-8') if isinstance(s, str) else s
    return encode_varint(tag) + encode_varint(len(b_s)) + b_s

class GatewayHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else '{}'
        try:
            data = json.loads(body)
            jwt = data.get('gametoken', '')
            sid = data.get('sid', '')
            
            pb = encode_pb_string(1, jwt) + encode_pb_string(2, sid)
            b64_url = base64.urlsafe_b64encode(pb).decode('utf-8').rstrip('=')
            
            resp_data = json.dumps({"status": "success", "data": b64_url}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(resp_data)
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

if __name__ == '__main__':
    print("[+] Vanguard Gateway Relay running locally on http://127.0.0.1:8080/gw.php")
    server = HTTPServer(('127.0.0.1', 8080), GatewayHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
