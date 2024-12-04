#version 460 core

out vec4 FragColor;

in vec3 FragPos;  // 从顶点着色器传来的片段位置
in vec3 Normal;   // 从顶点着色器传来的法向量
in vec2 TexCoords; // 从顶点着色器传来的纹理坐标

uniform vec3 lightPos;  // 光源位置
uniform vec3 lightColor; // 光源颜色
uniform vec3 viewPos;   // 摄像机位置
uniform sampler2D texture1; // 纹理采样器

void main()
{
    // 环境光
    vec3 ambient = 0.1 * lightColor;

    // 漫反射光
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    // 镜面反射光 (Phong 光照)
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = spec * lightColor * 0.5; // 镜面反射强度

    vec3 result = (ambient + diffuse + specular) * texture(texture1, TexCoords).rgb;
    FragColor = vec4(result, 1.0);
}
