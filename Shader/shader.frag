#version 330 core

in vec3 FragPos;  // 从顶点着色器传递的片段位置
in vec3 Normal;   // 从顶点着色器传递的片段法线
in vec2 TexCoords; // 从顶点着色器传递的纹理坐标

out vec4 FragColor;  // 输出的颜色

uniform vec3 lightPos;  // 光源位置
uniform vec3 viewPos;   // 观察者（相机）位置
uniform vec3 lightColor; // 光源颜色
uniform vec3 objectColor; // 物体颜色
uniform sampler2D texture1; // 物体纹理

void main()
{
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);

    vec3 ambient = 0.1 * lightColor;
    vec3 diffuse = diff * lightColor;

    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = 0.5 * spec * lightColor;

    vec3 result = (ambient + diffuse + specular) * objectColor;
    vec4 texColor = texture(texture1, TexCoords);
    FragColor = vec4(result, 1.0) * texColor;
}
