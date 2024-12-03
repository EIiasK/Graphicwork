#version 330 core
layout(location = 0) in vec3 aPos;  // 顶点位置
layout(location = 1) in vec3 aNormal; // 顶点法线
layout(location = 2) in vec2 aTexCoords; // 纹理坐标

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoords = aTexCoords;
    gl_Position = projection * view* model * vec4(FragPos, 1.0);
}

