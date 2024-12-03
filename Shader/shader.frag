#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;

out vec4 FragColor;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor;
uniform sampler2D texture1;

void main() {
    // 光照计算
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    vec3 ambient = 0.1 * lightColor;
    vec3 result = (ambient + diffuse) * objectColor;

    // 如果有纹理，可以结合纹理颜色
    // vec4 texColor = texture(texture1, TexCoords);
    // result *= texColor.rgb;

    FragColor = vec4(result, 1.0);
}
