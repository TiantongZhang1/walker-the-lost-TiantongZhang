shader_type spatial;

uniform sampler2D stone_albedo : source_color, filter_linear_mipmap;
uniform sampler2D wetness_mask : filter_linear_mipmap, hint_default_black;

group_uniforms surface;
uniform vec3 tint : source_color = vec3(1.0);
uniform float roughness_dry : hint_range(0.0, 1.0) = 0.85;

group_uniforms water;
uniform float water_darkening : hint_range(0.0, 1.0) = 0.55;
uniform float water_roughness : hint_range(0.0, 1.0) = 0.08;
group_uniforms;

void fragment() {
	// 遮罩：0 表示干燥，1 表示完全湿润。
	float w = texture(wetness_mask, UV).r;

	// 石头本色乘上颜色调整。
	vec3 base = texture(stone_albedo, UV).rgb * tint;

	// 越湿越暗。
	ALBEDO = base * (1.0 - w * water_darkening);

	// 根据湿度，在干燥和湿润粗糙度之间插值。
	ROUGHNESS = mix(roughness_dry, water_roughness, w);
}