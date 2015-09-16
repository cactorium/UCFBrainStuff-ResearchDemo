#version 300 es

layout(location = 0) in vec3 vertexPosition_modelspace;

out vec2 fragCoord;

void main() {
    gl_Position.xyz = vertexPosition_modelspace;
    gl_Position.w = 1.0;

    fragCoord = gl_Position.xy;
}
