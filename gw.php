<?php
header('Content-Type: application/json');

// Read JSON input from POST request
$raw_input = file_get_contents('php://input');
$json = json_decode($raw_input, true);

if (!$json || !isset($json['gametoken'])) {
    echo json_encode([
        'status' => 'error',
        'code' => 400,
        'message' => 'Missing gametoken parameter'
    ]);
    exit;
}

$gametoken = $json['gametoken'];
$sid = isset($json['sid']) ? $json['sid'] : '';

// Helper to encode varint for Protobuf
function encode_varint($value) {
    $buf = '';
    while ($value >= 0x80) {
        $buf .= chr(($value & 0x7F) | 0x80);
        $value >>= 7;
    }
    $buf .= chr($value & 0x7F);
    return $buf;
}

// Helper to encode Protobuf string field
function encode_pb_string($field_num, $str) {
    if (empty($str)) return '';
    $tag = ($field_num << 3) | 2;
    return encode_varint($tag) . encode_varint(strlen($str)) . $str;
}

// Build Protobuf binary payload
$pb = encode_pb_string(1, $gametoken);
if (!empty($sid)) {
    $pb .= encode_pb_string(2, $sid);
}

// Base64URL encode payload matching C++ b64_url_decode logic
$b64 = base64_encode($pb);
$b64_url = str_replace(['+', '/', '='], ['-', '_', ''], $b64);

echo json_encode([
    'status' => 'success',
    'data' => $b64_url
]);
