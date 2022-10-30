#ifndef COYOMI_CONFIG_H
#define COYOMI_CONFIG_H

#define DEFAULT_LOG_DIR "/home/kaz/log_data"
#define DEFAULT_ROOT "/home/kaz/coyomi"

#define SIM_TIME_SPEED 5.0 				// シミュレータの更新速度の倍速指定
#define LOCALIZATION_TIME_STEP 100000 	// 自己位置推定の時間刻み幅[usec]
#define NAVIGATION_TIME_STEP 100000 	// ナビゲーションの時間刻み幅[usec]
#define SIM_VIEWER_TIME_STEP 500000 	// SIM_VIEWER更新時間刻み幅[usec]

#define WHITE255 cv::Scalar(255, 255, 255)
#define BLUE255 cv::Scalar(255, 0, 0)
#define BLACK0 cv::Scalar(0, 0, 0)

#define HUGE_VALUE 99999999

#define RAD2DEG(a) a * 180.0 / M_PI
#define DEG2RAD(a) a * M_PI / 180.0

#endif // COYOMI_CONFIG_H
