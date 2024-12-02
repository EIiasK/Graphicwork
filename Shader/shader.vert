#version 330 core

layout(location = 0) in vec3 aPos;  // 顶点位置
layout(location = 1) in vec3 aNormal; // 顶点法线
layout(location = 2) in vec2 aTexCoords; // 纹理坐标

out vec3 FragPos;  // 传递到片段着色器的片段位置
out vec3 Normal;   // 传递到片段着色器的片段法线
out vec2 TexCoords; // 传递到片段着色器的纹理坐标

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    FragPos = vec3(model * vec4(aPos, 1.0)); // 计算物体在世界空间中的位置
    Normal = mat3(transpose(inverse(model))) * aNormal; // 计算物体法线
    TexCoords = aTexCoords;  // 传递纹理坐标

    gl_Position = projection * view * vec4(FragPos, 1.0); // 将顶点位置转换到裁剪空间
}
