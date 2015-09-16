#version 300 es

uniform uint vals;

in highp vec2 fragCoord;
out highp vec3 color;
 
void main(){
    uint mask = 0x00000001u;
    mask = (fragCoord.x < 0.0f) ? mask : (mask << 1);
    mask = (abs(fragCoord.x) < 0.5f) ? mask : (mask << 2);
    mask = (fragCoord.y < 0.0f) ? mask : (mask << 4);
    mask = (abs(fragCoord.y) < 0.5f) ? mask : (mask << 8);

    if ((vals & mask) != 0u) {
        color = vec3(1.0f, 1.0f, 1.0f);
    } else {
        color = vec3(0.0f, 0.0f, 0.0f);
    }
}
