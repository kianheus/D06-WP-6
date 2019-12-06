''' This script calculates the deflection and twist of a wing box cross section'''
# Keeping time and imports ------------------------------------------------------------------
import time
start_time = time.time()

import math
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy import interpolate
from scipy import integrate

# Inputs ------------------------------------------------------------------------------------


# Given by the previous iterations
C_r = round(3.695625413,4)           # Root chord            [m]
C_t = round(1.107118055,4)           # Tip chord             [m]
b = round(24.01371734,4)             # Wing span             [m]
x_frontspar = 0.20          # Front spar position   [%]
x_rearspar = 0.60           # Rear spar position    [%]
h_frontspar = 0.0908        # Front spar height     [%]
h_rearspar = 0.0804         # Rear spar height      [%]
T_engine = 21244            # Engine thrust         [N] FILLER
V = 228.31                  # Max speed             [m/s]

n = 2.5 * 1.5               # Load factor           [-]

# --------------------
# ---DESIGN CHOICES---
# --------------------

# Material properties (Al-4047)
E = 72 * 10**9              # E-modulus of material [Pa]
G = 27 * 10**9              # G-modulus of material [Pa]
rho = 2660                  # Density of material   [kg/m^3]

# Thickness and area design choices                 [FILLERS]
t_sheet_spar = 0.0005       # Spar thickness        [m]
t_sheet_hor = 0.0085        # Horizontal sheets thickness [m]

# Stringer area as a function of the geometry (hat stringer)
#        w_top_side_stringer
#      <----->
#      ______         ^
#     |      |        | h_stringer
#  ___|      |___     v
#  <-->
#  w_sides_stringer

t_stringer = 0.002          # Thickness stringer [m]
h_stringer = 0.05           # Height of stringer [m]
w_sides_stringer = 0.01     # Width of the sides of the stringer [m]
w_top_side_stringer = 0.05  # Width of the top side of the stringer [m]
A_str = t_stringer*(2*h_stringer + 2*w_sides_stringer + w_top_side_stringer)-4*t_stringer*t_stringer      # Area of a stringer [m^2]

# Stringers design choices                          [FILLERS]
''' To insert stringers on your desired location, you first set the intervals at which
the stringers will vary, using distance_top. Then in the stringers_top array you input
the stringer location as % of the chord. With a spacing of [0.25, 0.5, 1] for example,
and locations [[0.2, 0.2, 0.2], [0.4, 0.4, 0], [0.6, 0, 0], [0.8, 0.8, 0.8]], there
will be 4 stringers located at [0.2, 0.4, 0.6, 0.8] percent of the chord up until 25%
of the span. Then until 50% it will look like [0.2, 0.4, 0.8] etc.'''

distance_top = np.array([0.5, 1])                        # Interval of stringer variance [%span]
stringers_top = np.array([[0.1, 0.1], [0.35,  0],[0.6, 0], [1, 1]])
topstr = sp.interpolate.interp1d(distance_top,stringers_top,kind='next',fill_value='extrapolate')

distance_bot = np.array([0.4, 0.6, 1])                        # Interval of stringer variance [%span]
stringers_bot = np.array([[0.1, 0.1, 0.1],[0.35,0,0],[0.65,0,0],[1, 1, 1]])
botstr = sp.interpolate.interp1d(distance_bot,stringers_bot,kind='next',fill_value='extrapolate')


# Lift and moment distribution --------------------------------------------------------------

Ldistr = [14738.69053365474, 14738.833233974943, 14739.261212029445, 14739.974099099943, 14740.971280655951, 14742.25189635477, 14743.814840041492, 14745.658759749034, 14747.782057698092, 14750.18289029718, 14752.85916814261, 14755.80855601848, 14759.028472896709, 14762.51609193699, 14766.268340486853, 14770.281900081602, 14774.553206444345, 14779.078449486005, 14783.853573305296, 14788.874276188719, 14794.136010610604, 14799.633898801843, 14805.35806603624, 14811.291315802595, 14817.415859967912, 14823.713951024658, 14830.167906784747, 14836.760134171456, 14843.473152109502, 14850.289613513083, 14857.192326371935, 14864.164273935477, 14871.188633994974, 14878.24879726368, 14885.328384855102, 14892.411264859242, 14899.481568016865, 14906.523702491822, 14913.522367741434, 14920.462567484848, 14927.329621769462, 14934.109178135384, 14940.787221877927, 14947.350085408103, 14953.784456711202, 14960.077386903393, 14966.216296886274, 14972.18898309963, 14977.983622372027, 14983.588775869588, 14988.993392142735, 14994.186809270946, 14999.158756105653, 15003.899352610999, 15008.399109302816, 15012.64892578546, 15016.640088386854, 15020.364266891416, 15023.813510371085, 15026.980242114425, 15029.857253653654, 15032.437697889778, 15034.715092415496, 15036.686796782864, 15038.35877771189, 15039.738142218333, 15040.831859775919, 15041.646765024692, 15042.189560398061, 15042.466818668237, 15042.484985410358, 15042.250381385025, 15041.769204839495, 15041.047533727358, 15040.091327846776, 15038.906430897285, 15037.498572455124, 15035.873369867099, 15034.036330063029, 15031.992851286686, 15029.74822474541, 15027.307636178, 15024.676167341506, 15021.85879741629, 15018.860404329722, 15015.685765998496, 15012.339561489356, 15008.826372098472, 15005.150682349347, 15001.316880909215, 14997.32926142404, 14993.192023272048, 14988.909272235802, 14984.485021092774, 14979.92319012463, 14975.227607544788, 14970.402009844802, 14965.45004205912, 14960.375257948399, 14955.181120101484, 14949.870999955781, 14944.448177736289, 14938.915842313098, 14933.277048397824, 14927.533303959617, 14921.684298649512, 14915.729631282438, 14909.668921816317, 14903.501811422017, 14897.227962548452, 14890.847058983129, 14884.358805908003, 14877.762929950606, 14871.059179230553, 14864.24732340141, 14857.327153687787, 14850.29848291786, 14843.161145551161, 14835.914997701751, 14828.559917156683, 14821.095803389775, 14813.522577570764, 14805.8401825698, 14798.048582957153, 14790.147764998383, 14782.13773664482, 14774.018527519269, 14765.790188897152, 14757.452793682947, 14749.00643638196, 14740.451233067384, 14731.78732134276, 14723.01486029969, 14714.134030470987, 14705.145033778977, 14696.048093479358, 14686.843454100197, 14677.531381376328, 14668.112162179114, 14658.58610444149, 14648.95353707833, 14639.214809902205, 14629.370293534379, 14619.420382199653, 14609.365621926698, 14599.20674767772, 14588.94449986413, 14578.579609965504, 14568.11280056146, 14557.544785362828, 14546.876269242208, 14536.107948263878, 14525.240509713058, 14514.27463212448, 14503.210985310418, 14492.05023038791, 14480.793019805482, 14469.43999736916, 14457.991798267785, 14446.449049097784, 14434.812367887229, 14423.082364119224, 14411.259638754718, 14399.344784254608, 14387.338384601215, 14375.241015319109, 14363.053243495317, 14350.775627798796, 14338.40871849938, 14325.953057485978, 14313.409178284148, 14300.777606073054, 14288.058857701773, 14275.253441704914, 14262.36185831759, 14249.3845994898, 14236.322148900113, 14223.174981968705, 14209.943565869778, 14196.628359543269, 14183.229813706006, 14169.748370862142, 14156.184464796757, 14142.538480604031, 14128.810730206189, 14115.001519294328, 14101.111154417906, 14087.139942981272, 14073.08819324008, 14058.956214297774, 14044.744316102004, 14030.452809441113, 14016.08200594054, 14001.632218059272, 13987.103759086265, 13972.496943136874, 13957.812085149259, 13943.049500880801, 13928.209506904543, 13913.292420605525, 13898.298560177236, 13883.228244617994, 13868.081793727308, 13852.859528102279, 13837.561769133992, 13822.188839003842, 13806.74106067993, 13791.21875791343, 13775.622255234915, 13759.951877950718, 13744.207952139288, 13728.390804647506, 13712.500763087057, 13696.538155830693, 13680.503312008614, 13664.396561504762, 13648.218234953141, 13631.968663734116, 13615.648179970705, 13599.257116524897, 13582.795804536081, 13566.264507751788, 13549.66341445808, 13532.992707989735, 13516.25257057808, 13499.443183352842, 13482.564726343968, 13465.617378483395, 13448.601317606881, 13431.516720455735, 13414.363762678611, 13397.142618833253, 13379.85346238823, 13362.49646572464, 13345.071800137866, 13327.579635839227, 13310.020141957712, 13292.393486541623, 13274.699836560234, 13256.939357905465, 13239.112215393514, 13221.21857276647, 13203.258592693923, 13185.23243677457, 13167.140265537812, 13148.982238445311, 13130.758513892573, 13112.469249210459, 13094.114600666773, 13075.69472346773, 13057.209771759537, 13038.659898629823, 13020.045256109164, 13001.365995172539, 12982.622265740822, 12963.814216682193, 12944.941995801246, 12926.00574103118, 12907.00556570157, 12887.941579855476, 12868.81389453691, 12849.622621789806, 12830.367874657102, 12811.04976717974, 12791.668414395675, 12772.223932338888, 12752.716438038362, 12733.146049517089, 12713.512885791037, 12693.81706686812, 12674.05871374714, 12654.237948416789, 12634.354893854521, 12614.409674025517, 12594.402413881648, 12574.333239360316, 12554.20227738343, 12534.009655856242, 12513.75550366631, 12493.439950682297, 12473.063127752896, 12452.625166705697, 12432.126200346007, 12411.56636245572, 12390.945787792154, 12370.26461208686, 12349.522972044475, 12328.721005341496, 12307.858850625113, 12286.936647511975, 12265.954536587016, 12244.912653116733, 12223.81101370807, 12202.649529232584, 12181.428108679189, 12160.146662966614, 12138.805104944127, 12117.403349392334, 12095.94131302392, 12074.41891448446, 12052.836074353185, 12031.192715143865, 12009.488761305578, 11987.7241392236, 11965.898777220269, 11944.012605555887, 11922.065556429548, 11900.057563980165, 11877.988564287283, 11855.858495372126, 11833.66729719849, 11811.414911673763, 11789.101282649908, 11766.726355924453, 11744.29007924156, 11721.792402293022, 11699.233276719342, 11676.612656110832, 11653.930496008645, 11631.186753905919, 11608.381389248905, 11585.51436343809, 11562.585639829338, 11539.59518373507, 11516.542914809761, 11493.428526204774, 11470.251647863517, 11447.011916218786, 11423.708974206344, 11400.342471264292, 11376.912063332376, 11353.41741285129, 11329.858188761918, 11306.234066504563, 11282.54472801811, 11258.789861739195, 11234.969162601266, 11211.082332033708, 11187.12907796081, 11163.10911480083, 11139.0221634649, 11114.867951355973, 11090.646212367677, 11066.356686883222, 11041.999121774135, 11017.57327039911, 10993.07889260267, 10968.515754713942, 10943.883629545247, 10919.182296390796, 10894.411541025225, 10869.571155702171, 10844.66093915279, 10819.680696584232, 10794.630219263643, 10769.508917019919, 10744.315862675548, 10719.050130316537, 10693.710807691607, 10668.296996215027, 10642.807810969678, 10617.242380710219, 10591.59984786653, 10565.879368547177, 10540.08011254314, 10514.201263331708, 10488.242018080457, 10462.201587651507, 10436.079196605851, 10409.874083207893, 10383.58549943015, 10357.212710958118, 10330.754997195267, 10304.211651268306, 10277.581980032446, 10250.865304077013, 10224.06095773107, 10197.16828906933, 10170.186659918127, 10143.115445861646, 10115.954036248244, 10088.701834196985, 10061.358194424012, 10033.921405863033, 10006.388871938803, 9978.758008515008, 9951.026273241978, 9923.191165549475, 9895.250226638494, 9867.201039472184, 9839.041228765764, 9810.768460975569, 9782.380444287153, 9753.874928602394, 9725.249705525763, 9696.502608349563, 9667.631512038322, 9638.634333212156, 9609.509030129306, 9580.253602667617, 9550.866092305201, 9521.344582100102, 9491.687196669012, 9461.892102165097, 9431.957506254868, 9401.881658094127, 9371.662848302934, 9341.299405718435, 9310.788897667282, 9280.127092943083, 9249.309574827997, 9218.332004006836, 9187.190118560617, 9155.879733960428, 9124.396743061792, 9092.737116099277, 9060.89690068155, 9028.872221786785, 8996.659281758422, 8964.254360301378, 8931.653814478484, 8898.854078707462, 8865.851664758144, 8832.643161750135, 8799.225236150829, 8765.594631773783, 8731.748169777478, 8697.682748664465, 8663.395344280843, 8628.883009816165, 8594.14218645146, 8559.158776480854, 8523.910586093509, 8488.37554994276, 8452.531958594647, 8416.358458602994, 8379.83405259788, 8342.938099387646, 8305.65031407426, 8267.950768182249, 8229.819889800989, 8191.238463740513, 8152.187631700758, 8112.648892454277, 8072.604102042381, 8032.035473984791, 7990.925579502668, 7949.257347755209, 7907.014066089566, 7864.179380304367, 7820.737379292202, 7776.672932325573, 7731.971395308793, 7686.618477818593, 7640.600242787418, 7593.903106210749, 7546.5138368333355, 7498.419555814425, 7449.607736371903, 7400.06620340542, 7349.78313309842, 7298.747052499173, 7246.94683908073, 7194.3717202798025, 7141.011273014676, 7086.855423181956, 7031.892865128056, 6976.015352461269, 6918.96467703738, 6860.473833220557, 6800.280445789881, 6738.12677053031, 6673.759695173632, 6606.930740689371, 6537.396062925709, 6464.916454600346, 6389.257347641371, 6310.188815878078, 6227.485578081775, 6140.927001356565, 6050.351146684719, 5955.8764548301015, 5857.708606965213, 5756.050755350717, 5651.103477666071, 5543.064772436339, 5432.130054779042, 5318.492152470725, 5202.341302333567, 5083.865146941703, 4962.584246743782, 4832.726979812208, 4686.089844460467, 4514.603426217156, 4310.348850563214, 4065.5579732683823, 3772.6136411895773, 3424.05002353075, 3012.553013564782, 2530.960700816709]
Mdistr = [-12818.965824500854, -12818.169048764714, -12815.778918943763, -12811.796027159826, -12806.221360147321, -12799.056299050348, -12790.302619138547, -12779.96248944188, -12768.03847230414, -12754.533522855374, -12739.450988403085, -12722.794607742233, -12704.568510384168, -12684.77721570429, -12663.425632008595, -12640.519055519007, -12616.063169277599, -12590.06404196956, -12562.528126665065, -12533.46225947994, -12502.873658155166, -12470.770290288252, -12437.181370611872, -12402.16790941547, -12365.793495626911, -12328.121603039996, -12289.215547878666, -12249.13844819084, -12207.953185075809, -12165.722365746798, -12122.508288429299, -12078.372909093903, -12033.377810021175, -11987.584170194348, -11941.052737514912, -11893.843802834293, -11846.017175794002, -11797.632162465552, -11748.747544780214, -11699.421561737752, -11649.711892382536, -11599.675640534411, -11549.369321261012, -11498.848849077474, -11448.169527858918, -11397.3860424505, -11346.5524519592, -11295.722184711361, -11244.94803485926, -11194.28216062008, -11143.776084130153, -11093.480692897196, -11043.446242833494, -10993.722362852315, -10944.358061010747, -10895.401732181292, -10846.901167235714, -10798.903563723974, -10751.455538032053, -10704.603139002613, -10658.391863002713, -10612.866670423678, -10568.071947223209, -10524.033708780074, -10480.73452104661, -10438.150776975364, -10396.259153855504, -10355.036606119489, -10314.460358394183, -10274.507898793117, -10235.156972447587, -10196.385575273522, -10158.171947971745, -10120.494570259076, -10083.332155327598, -10046.66364452993, -10010.46820228799, -9974.725211222987, -9939.414267504506, -9904.515176416295, -9870.007948136978, -9835.872793733099, -9802.09012136311, -9768.64053268971, -9735.504819498956, -9702.663960524193, -9670.099118472755, -9637.791637253864, -9605.723039405711, -9573.875023720024, -9542.229463062386, -9510.768402386579, -9479.47405694123, -9448.328810667013, -9417.315214782962, -9386.415986559854, -9355.614008279466, -9324.892326377703, -9294.234150770126, -9263.622854358315, -9233.041972715238, -9202.475203948205, -9171.906408737614, -9141.319854821897, -9110.70837381414, -9080.075184440686, -9049.424113337102, -9018.758956631766, -8988.083479834233, -8957.401417733017, -8926.71647430284, -8896.03232262127, -8865.352604794616, -8834.680931893112, -8804.02088389526, -8773.376009641253, -8742.749826795474, -8712.145821817916, -8681.567449944585, -8651.01813517664, -8620.501270278364, -8590.02021678378, -8559.578305011964, -8529.178834090797, -8498.82507198931, -8468.520255558404, -8438.267590579877, -8408.070251823756, -8377.931383113855, -8347.8540974014, -8317.841476846741, -8287.896572909094, -8258.022406444124, -8228.221967809433, -8198.498216977769, -8168.854083658014, -8139.292467423739, -8109.8162378493225, -8080.428234653621, -8051.131267851014, -8021.928117909786, -7992.821535917861, -7963.814243755677, -7934.908896992398, -7906.106392905, -7877.405197425283, -7848.803609850352, -7820.29994530388, -7791.892534646227, -7763.579724386179, -7735.35987659426, -7707.23136881766, -7679.1925939967705, -7651.241960383166, -7623.377891459286, -7595.5988258595125, -7567.903217292854, -7540.289534467126, -7512.75626101455, -7485.30189541897, -7457.924950944406, -7430.623955565137, -7403.397451897207, -7376.2439971313515, -7349.162162967351, -7322.150535549777, -7295.207715405155, -7268.332317380453, -7241.522970582994, -7214.77831832168, -7188.097018049554, -7161.4777413077145, -7134.919173670538, -7108.420014692168, -7081.978977854334, -7055.59479051541, -7029.266193860771, -7002.991942854361, -6976.770806191542, -6950.601566253093, -6924.483019060506, -6898.413974232442, -6872.393260739422, -6846.420183732867, -6820.494847656357, -6794.617433906642, -6768.788122437982, -6743.0070917634375, -6717.274518956126, -6691.590579650513, -6665.955448043759, -6640.369296897057, -6614.832297536992, -6589.344619856943, -6563.906432318508, -6538.517901952909, -6513.179194362489, -6487.89047372218, -6462.651902781016, -6437.463642863634, -6412.325853871867, -6387.2386942862895, -6362.202321167804, -6337.216890159284, -6312.282555487204, -6287.399469963282, -6262.567784986171, -6237.787650543187, -6213.059215211994, -6188.382626162364, -6163.758029157959, -6139.185568558104, -6114.66538731961, -6090.197626998577, -6065.782427752274, -6041.419928340996, -6017.110266129968, -5992.853577091247, -5968.649995805653, -5944.49965546473, -5920.402682347251, -5896.359049198842, -5872.368561642304, -5848.431018758032, -5824.5462217720315, -5800.713974048037, -5776.9340810796375, -5753.2063504824355, -5729.530591986252, -5705.906617427356, -5682.334240740703, -5658.81327795225, -5635.343547171269, -5611.924868582676, -5588.557064439446, -5565.23995905499, -5541.9733787956275, -5518.757152073033, -5495.591109336729, -5472.47508306663, -5449.408907765601, -5426.392419952011, -5403.425458152365, -5380.507862893933, -5357.639476697422, -5334.820144069657, -5312.049711496301, -5289.328027434587, -5266.654942306113, -5244.030308489601, -5221.453980313749, -5198.925814050043, -5176.445667905647, -5154.0134020162795, -5131.628878439136, -5109.291961145839, -5087.00251606249, -5064.760445094265, -5042.565745586995, -5020.4184314660315, -4998.318517024028, -4976.266016916365, -4954.260946156606, -4932.303320111899, -4910.393154498416, -4888.530465376761, -4866.715269147371, -4844.947582545934, -4823.227422638765, -4801.554806818225, -4779.929752798073, -4758.352278608887, -4736.822402593399, -4715.340143401869, -4693.905519987499, -4672.518551601726, -4651.179257789629, -4629.88765838524, -4608.643773506932, -4587.447623552717, -4566.299229195621, -4545.198611378999, -4524.145791311867, -4503.140790464235, -4482.183630562422, -4461.274333584383, -4440.4129217550235, -4419.5994175415035, -4398.83384364855, -4378.116223013781, -4357.446578802992, -4336.824931552599, -4316.251247858063, -4295.725446774405, -4275.2474471581345, -4254.817169392807, -4234.434535380891, -4214.099468535692, -4193.811893773246, -4173.571737504249, -4153.378927625964, -4133.233393514196, -4113.135066015205, -4093.0838774376766, -4073.0797615446995, -4053.1226535457454, -4033.212490088615, -4013.3492092514957, -3993.5327505349037, -3973.763054853739, -3954.0400645292843, -3934.363723281241, -3914.7339762197635, -3895.1507698375003, -3875.6140520016556, -3856.1237719460364, -3836.6798802631192, -3817.2823288961436, -3797.9310711311655, -3778.6260615891583, -3759.3672562181087, -3740.154612285115, -3720.9880883684896, -3701.8676443498653, -3682.793231773169, -3663.764757560508, -3644.782117646307, -3625.845211157308, -3606.9539403913573, -3588.108210793288, -3569.30793093079, -3550.553012470242, -3531.843370152555, -3513.1789217689775, -3494.559588136889, -3475.9852930755756, -3457.455963381986, -3438.971528806489, -3420.5319220285833, -3402.1370786326293, -3383.786937083528, -3365.4814387024194, -3347.220527642333, -3329.0041508638715, -3310.8322581108146, -3292.7048018857868, -3274.621737425838, -3256.583022678073, -3238.588618275224, -3220.638487511249, -3202.732596316878, -3184.8709132351933, -3167.0534093971555, -3149.2800584971656, -3131.550833606264, -3113.8656503543193, -3096.22437431669, -3078.626873591727, -3061.073020692456, -3043.5626925144475, -3026.0957703037634, -3008.6721396249086, -2991.2916903288747, -2973.954316521167, -2956.659916529884, -2939.408392873868, -2922.199652230833, -2905.0336054055783, -2887.9101672981956, -2870.82925687233, -2853.790797123466, -2836.7947150472405, -2819.840941607777, -2802.9294117060763, -2786.060064148382, -2769.232841614619, -2752.4476906268337, -2735.7045615176557, -2719.003408398789, -2702.344189129512, -2685.7268652852135, -2669.1514021259277, -2652.6177433683474, -2636.125400531671, -2619.6735321740243, -2603.2613099504256, -2586.887930336342, -2570.5526144196206, -2554.2546076918884, -2537.9931798393513, -2521.767624533079, -2505.5772592187486, -2489.4214249058828, -2473.2994859565524, -2457.2108298736403, -2441.15486708856, -2425.131030748577, -2409.13877650362, -2393.1775822926975, -2377.246948129851, -2361.346395889722, -2345.4754690927152, -2329.633732689751, -2313.8207728466705, -2298.036196728272, -2282.279632281998, -2266.5507280212655, -2250.849153411797, -2235.1747478356324, -2219.5277102007226, -2203.908293503022, -2188.316755324957, -2172.753357763675, -2157.218367359296, -2141.712055023216, -2126.2346959664196, -2110.7865696278163, -2095.3679596026, -2079.979153570621, -2064.620443224805, -2049.292124199547, -2033.9944959991642, -2018.7278619263373, -2003.4925290105878, -1988.288807936753, -1973.1170129734842, -1957.9774619017555, -1942.8704759433906, -1927.7963796895804, -1912.7555010294404, -1897.747827386074, -1882.7680798526847, -1867.807015645103, -1852.8555569938824, -1837.9049024076492, -1822.9465241785342, -1807.9721658976875, -1792.9738399806727, -1777.9438252024188, -1762.8746642415178, -1747.7591612335357, -1732.5903793331424, -1717.3616382847315, -1702.066512001314, -1686.6988261513675, -1671.2526557534331, -1655.7223227781237, -1640.1023937573593, -1624.387677400467, -1608.5732222169763, -1592.657133685082, -1576.6516949149627, -1560.573265646543, -1544.4378003558961, -1528.2608500674964, -1512.0575657078664, -1495.8427014857111, -1479.630618297967, -1463.435287161168, -1447.270292667548, -1431.1488364652678, -1415.083740762223, -1399.0874518527878, -1383.172043666939, -1367.3492213411785, -1351.6303248106196, -1336.0255066784107, -1320.4939346139229, -1304.9173324184649, -1289.174449205858, -1273.1480634234304, -1256.7249413361938, -1239.7957958158197, -1222.255245425608, -1204.001773792689, -1184.9376892586522, -1164.9690847998345, -1144.0057982084627, -1121.9613725258678, -1098.7530167189718, -1074.3783414644056, -1049.2272771009032, -1023.801640045302, -998.586692495105, -974.0512581495526, -950.647898216132, -928.8130894643083, -908.967404264256, -891.5156925485526, -876.8472656346494, -865.0436455039114, -853.8588492215287, -840.0189968115786, -820.3604628682112, -791.8358311800829, -751.5126821571398, -696.5724313531506, -624.3092173419107, -532.1288372017822, -417.54772785866413]

# Calculation accuracy
points = len(Ldistr)        # Calculation accuracy  [-]
step = (b/2)/points         # Step size             [-]

# Moment distribution function --------------------------------------------------------------

# get internal moment distribution
def getMomentDistr(Ldistr,loadfactor):
    Ldistr[0] = 0
    #Ldistr.append(0)
    LdistrArr = -1 * np.array(Ldistr)
    Ldistr = list(LdistrArr*loadfactor)

    # input variables
    L = 12.009  # half wing span
    Lmax = 2500
    npoints = len(Ldistr) - 1
    dy = L / npoints

    # find p position
    Ppos = round(0.35 * npoints)

    def p(n, Ppos):
        if n == Ppos:
            return 20267
        else:
            return 0

    # calculate wing weight along y
    def W_w(y):
        return 391.2366 * (-0.215585 * y + 3.695654)

    W_w_distr = []
    for n in range(npoints + 1):
        W_w_distr.append(W_w((L / npoints) * n))
    W_w_distr[0] = 0
    W_w_distr[npoints] = 0

    halfWingWeight, error = sp.integrate.quad(W_w, 0, L)
    # calculate shear
    sumdistr = []
    for n in range(npoints + 1):
        sumdistr.append((W_w_distr[n] + round(Ldistr[n],3)))

    shear_internal_distr = []
    for n in range(npoints + 1):
        sum_integral = []
        for n_1 in range(n, npoints + 1):
            sum_integral.append((sumdistr[n_1] * dy + p(n_1, Ppos)))
        sum_contribution = sum(sum_integral)
        shear_internal_distr.append(sum_contribution)

    moment_internal_distr = []
    for n in range(npoints + 1):
        sum_integral = []
        for n_1 in range(n, npoints + 1):
            sum_integral.append((shear_internal_distr[n_1] * dy))
        sum_contribution = sum(sum_integral)
        moment_internal_distr.append(sum_contribution)

    # make graphs
    ytab = []
    for n in range(npoints + 1):
        ytab.append(n)

    return moment_internal_distr

# Torsion distribution function -------------------------------------------------------------

# get internal torsion distribution
def getTorsionDistribution(Ldistr, M_distr, rho, V, T, loadfactor):
    Ldistr = list(np.array(Ldistr)*loadfactor)
    # Define inputs
    def c(y):
        c = -0.21558573 * y + 3.6956254
        return c

    T = T * 0.8765588
    b_half = 12.009

    W_e = (2066 + (872.57 / 2)) * 9.81
    z_e = 0.7149
    x_e = 0.4661 + 0.15 * c(0.35 * b_half)
    y_e_ratio = 0.35

    # Along span
    npoints = len(Ldistr)
    y_e_point = round(npoints * y_e_ratio)

    c_distr = []
    for n in range(npoints):
        c_distr.append(c((b_half / npoints) * n))

    # Starting at wingtip
    torsion_distr = []
    for n in range(npoints):
        if abs(n - y_e_point) < 0.020833 * npoints:
            torsion_distr.append(
                (T * z_e - W_e * x_e) / (0.020833 * 2 * b_half) + round(Ldistr[n],3) * 0.15 * c_distr[n] + round(M_distr[n],3))
        else:
            torsion_distr.append(Ldistr[n] * 0.15 * c_distr[n] + round(M_distr[n],4))

    torsion_distr_new = []
    for n in range(npoints):
        if n > y_e_point:
            total_torsion = Ldistr[n] * 0.15 * c_distr[n] + round(M_distr[n],4)
            torsion_distr_new.append(total_torsion)
        else:
            total_torsion = Ldistr[n] * 0.15 * c_distr[n] + round(M_distr[n],4)
            torsion_distr_new.append(total_torsion)

    # Integrating
    dy = b_half / npoints

    torsion_int_distr = []

    def engine(n, T, z_e, W_e, x_e, y_e_point, npoints, b_half):
        if abs(n - y_e_point) < 0.020833 * npoints:
            return (T * z_e - W_e * x_e) / (0.020833 * 2 * b_half)
        else:
            return 0

    for n in range(npoints):
        sum_integral = []
        for n_1 in range(n, npoints):
            sum_integral.append(
                torsion_distr[n_1] * dy + engine(n_1, T, z_e, W_e, x_e, y_e_point, npoints, b_half) * dy)

        summation = sum(sum_integral)
        torsion_int_distr.append(summation)

    # Make graphs
    ytab = []
    for n in range(npoints):
        ytab.append(n)

    return torsion_int_distr

# Calculations of length, area & centroid ---------------------------------------------------

# Creating the steps and interval. This will decide the level
#   of detail of the calculations
y = np.linspace(0, b/2, points)
n_points = len(y)
C_y = C_r + C_t * (y/(b/2)) - C_r * (y/(b/2))   # Chord as function of y    [m]
ylst = y.tolist()

# Calculating the neutral axis, dividing the wing box plates into 4 parts
# Part length       [m]
L_I = (x_rearspar - x_frontspar) * C_y
L_II = h_rearspar * C_y
L_IV = h_frontspar * C_y
L_III = np.sqrt( (L_IV-L_II)**2 + L_I**2)

# Part area         [m^2]
A_I = L_I * t_sheet_hor
A_II = L_II * t_sheet_spar
A_III = L_III * t_sheet_hor
A_IV = L_IV * t_sheet_spar

# Part centroid     [m]
z_I = L_IV
z_II = L_IV - 0.5*L_II
z_III = 0.5 * (L_IV - L_II)
z_IV = 0.5 * L_IV

# Calculating the moment of inertia for the stringers----------------------------------------

n_iterations = len(y)

# Top stringers
y_n = 0
n_strlist_top = []

# This loop computes the # of stringers at each y coord
for i in range(n_iterations):
    n_str_y_n = len(topstr(y_n/(b/2))[topstr(y_n/(b/2)) != 0])
    y_n += step
    n_strlist_top.append(n_str_y_n)

n_str_top = np.array(n_strlist_top)

# Bottom stringers
y_n = 0
n_strlist_bot = []

# This loop computes the # of stringers at each y coord
for i in range(n_iterations):
    n_str_y_n = len(botstr(y_n/(b/2))[botstr(y_n/(b/2)) != 0])
    y_n += step
    n_strlist_bot.append(n_str_y_n)

n_str_bot = np.array(n_strlist_bot)

# z-coordinate of neutral axis, as seen from the bottom of the front spar
z_n = (A_str*(n_str_top)*z_I + A_str*(n_str_bot)*z_III + A_I*z_I + A_II*z_II + A_III*z_III + A_IV*z_IV) / (A_I + A_II + A_III + A_IV + A_str*(n_str_top+n_str_bot))

# Stringer MOI
# The stringer shape is assumed square
I_str_bot = n_str_bot * (A_str * (z_I-z_n)**2 + A_str**2 / 12)
I_str_top = n_str_top * (A_str * (z_I-z_n)**2 + A_str**2 / 12)

# Calculating the moment of inertia for the sheets-------------------------------------------


# Parts 1, 2 and 4
I_I = L_I * t_sheet_hor**3 * (1/12) + A_I * (z_I-z_n)**2
I_II = t_sheet_spar * L_II**3 * (1/12) + A_II * (z_II-z_n)**2
I_IV = t_sheet_spar * L_IV**3 * (1/12) + A_IV * (z_IV-z_n)**2

# Part 3 is slanted
I_III_x = L_III * t_sheet_hor**3 * (1/12)
I_III_y = t_sheet_hor * L_III**3 * (1/12)
theta_III = np.tan((L_IV-L_II)/L_I)

I_III = I_III_x * np.cos(theta_III)**2 + I_III_y * np.sin(theta_III)**2 + A_III * (z_III-z_n)**2

# Final MOI         [m^4]
I_str = I_str_top + I_str_bot
I = I_I + I_II + I_III + I_IV + I_str
I_lst = np.array(I).tolist()
AMOI = sp.interpolate.interp1d(y,I_lst,kind='cubic',fill_value='extrapolate')
I_plot = np.array(AMOI(y))

def I_y(y):
    return AMOI(y)

# OUTPUT: Moment of inertia as a function of y: I_y(y)
print('MOI done')

# Calculating the wing box mass -------------------------------------------------------------


# Individual sheets
M_I = (L_I[0] + L_I[-1]) / 2 * t_sheet_hor * b/2 * rho
M_II = (L_II[0] + L_II[-1]) / 2 * t_sheet_spar * b/2 * rho
M_III = (L_III[0] + L_III[-1]) / 2 * t_sheet_hor * b/2 * rho
M_IV = (L_IV[0] + L_IV[-1]) / 2 * t_sheet_spar * b/2 * rho

# Stringers

lentot = (np.sum(n_str_top) + np.sum(n_str_bot)) * b/2/n_points

M_str = lentot * A_str * rho

# Total mass
Mass = M_I + M_II + M_III + M_IV + M_str

# Calculating the torsional constant --------------------------------------------------------


A_encl = L_I*L_II + (L_IV-L_II)*L_I*0.5 - A_str*(n_str_bot+n_str_top) # Enclosed area [m^2]
ds_t = (L_I+L_III) / t_sheet_hor + (L_II+L_IV) / t_sheet_spar         # Integral of the reciprocal of t and length

J = 4 * A_encl**2 / ds_t                        # Torsional constant
T_C = sp.interpolate.interp1d(y,J,kind='cubic',fill_value='extrapolate')
J_plot = np.array(T_C(y))

def J_y(y):
    return T_C(y)

# OUTPUT: Torsional constant as a function of y: J_y(y)
print('J done')

# Moment and torque functions ---------------------------------------------------------------


M = getMomentDistr(Ldistr, n)
T = getTorsionDistribution(Ldistr, Mdistr, rho, V, T_engine, n)

# Calculating deflection --------------------------------------------------------------------


# Retrieving -M/EI
MEI = M/(E*I)

# First integration
MEIfunc = sp.interpolate.interp1d(y,MEI,kind='cubic',fill_value='extrapolate')
dvdylst = []

for i in range(n_iterations):
    dvdy = sp.integrate.quad(MEIfunc, ylst[i], (b/2))
    dvdylst.append(dvdy[0])

dvdy = np.array(dvdylst)

# Adding integration constant (because dvdy(0) = 0)
C_1 = -dvdy[0]
dvdy += C_1

print('First integration done')
# Second integration
dvdyfunc = sp.interpolate.interp1d(y,dvdy,kind='cubic',fill_value='extrapolate')
vlst = []

for i in range(n_iterations):
    v = sp.integrate.quad(dvdyfunc, ylst[i], (b/2))
    vlst.append(v[0])

v = np.array(vlst)

# Adding integration constant (because v(0) = 0)
C_2 = -v[0]
v += C_2
print('Second integration done')

# Calculating twist -------------------------------------------------------------------------


# Retrieving T/GJ
TGJ = T/(G*J)

# Integration
TGJfunc = sp.interpolate.interp1d(y,TGJ,kind='cubic',fill_value='extrapolate')
philst = []

for i in range(n_iterations):
    phi = sp.integrate.quad(TGJfunc, ylst[i], (b/2))
    philst.append(phi[0])

phi = np.array(philst)

# Adding integration constant (phi(0) = 0)

C_3 = -phi[0]
phi += C_3
print('Twist integration done')

# Statistics --------------------------------------------------------------------------------
v_max = np.amax(abs(v))
v_percentage = v_max/b * 100
phi_max = (np.amax(abs(phi)) * 180 / math.pi)

print(' ')
print('The wing box mass (half span) is', round(Mass, 2),'[kg]')
print('The maximum deflection is', round(v_max, 4), '[m] or', round(v_percentage, 3), '[%] of the span.')
print('The maximum twist is', round(phi_max, 4),'[deg]')
print("Calculations took %s seconds." % round((time.time() - start_time), 2))
plt.subplot(221)
plt.plot(y, v)
plt.subplot(222)
plt.plot(y, dvdy)
plt.subplot(224)
plt.plot(y, I)
plt.plot(y, I_str)
plt.subplot(223)
plt.plot(y, M)
#plt.plot(y, M)
plt.show()
