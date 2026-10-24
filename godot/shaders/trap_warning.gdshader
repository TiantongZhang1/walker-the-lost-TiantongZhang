shader_type canvas_item;
uniform float warn_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec3 warn_color: source_color = vec3(0.839216, 0.235294, 0.184314);

void fragment(){
COLOR.rgb = mix(COLOR.rgb, warn_color, warn_amount);
}