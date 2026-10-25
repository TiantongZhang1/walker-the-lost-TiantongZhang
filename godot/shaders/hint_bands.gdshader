shader_type spatial;
render_mode unshaded;

uniform sampler2D bands_srgb : source_color, filter_nearest;
uniform sampler2D bands_data : filter_nearest;

uniform bool use_source_color = true;

void fragment() {
	if (use_source_color) {
		ALBEDO = texture(bands_srgb, UV).rgb;
	} else {
		ALBEDO = texture(bands_data, UV).rgb;
	}
}