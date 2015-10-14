#version 300 es

uniform uint vals;
uniform uint chosen;

in highp vec2 fragCoord;
out highp vec3 color;
 
void main(){
    uint mask = 0x00000001u;
    uint val = 0u;
    val = (fragCoord.x < 0.0f) ? val : (val + 1u);
    val = (abs(fragCoord.x) < 0.5f) ? val : (val + 2u);
    val = (fragCoord.y < 0.0f) ? val : (val + 4u);
    val = (abs(fragCoord.y) < 0.5f) ? val : (val + 8u);
    mask = mask << val;

    if ((vals & mask) != 0u) {
        color = vec3(1.0f, 1.0f, 1.0f);
    } else {
        color = vec3(0.0f, 0.0f, 0.0f);
    }
    if (val == chosen) {
        if ((vals & mask) != 0u) {
            color = vec3(1.0f, 1.0f, 0.0f);
        }
    }
}
