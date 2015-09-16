#version 300 es

in highp vec2 fragCoord;
out highp vec3 color;
 
void main(){
    if (fragCoord.x < 0.0f) {
        color = vec3(1.0f, 1.0f, 0.0f);
    } else {
        color = vec3(1.0f, 0.0f, 1.0f);
    }
}
