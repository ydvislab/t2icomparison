"""Preset bipolar aspects: score = CLIP sim(image, right) - CLIP sim(image, left). Same text, same scale for every group."""
ASPECTS = [
    dict(key="light", cn="光线", left="cool blue light", right="warm golden light", lcn="冷色蓝光", rcn="暖色金光"),
    dict(key="tone", cn="色调", left="modern photo with natural neutral colors", right="vintage photo with sepia brown tones", lcn="自然中性", rcn="复古棕褐"),
    dict(key="sat", cn="饱和度", left="muted desaturated colors", right="vivid saturated colors", lcn="低饱和", rcn="高饱和"),
    dict(key="time", cn="时间", left="daytime", right="night", lcn="白天", rcn="夜晚"),
    dict(key="shot", cn="景别", left="extreme close-up", right="wide shot from far away", lcn="极近特写", rcn="远景"),
    dict(key="center", cn="构图", left="subject centered in a symmetric composition", right="subject off-center in an asymmetric composition", lcn="居中对称", rcn="偏离中心"),
    dict(key="angle", cn="视角", left="eye-level view", right="high angle view from above", lcn="平视", rcn="俯视"),
    dict(key="medium", cn="媒介", left="a photograph", right="a painting or illustration", lcn="照片", rcn="绘画插画"),
    dict(key="style", cn="风格", left="realistic", right="stylized", lcn="写实", rcn="风格化"),
    dict(key="bg", cn="背景", left="plain simple background", right="busy detailed background", lcn="简洁", rcn="繁杂"),
    dict(key="quality", cn="画质", left="professional polished photo", right="amateur casual snapshot", lcn="专业精修", rcn="业余随手拍"),
    dict(key="dof", cn="景深", left="blurry background with bokeh", right="everything in sharp focus", lcn="背景虚化", rcn="全部清晰"),
    dict(key="inout", cn="室内外", left="indoors", right="outdoors", lcn="室内", rcn="室外"),
    dict(key="clean", cn="整洁度", left="clean tidy scene", right="messy cluttered scene", lcn="整洁", rcn="杂乱"),
    dict(key="mood", cn="氛围", left="bright cheerful mood", right="dark moody atmosphere", lcn="明快", rcn="阴郁"),
]
