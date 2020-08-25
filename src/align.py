import numpy as np
import cv2
import sys, os


def draw_match_rect(image, corners, color=(255,255,255)):
	cv2.polylines(image, corners, True, color)


def draw_match_line(image, x1, x2, y1, y2, r, color=(0,255,0)):
	cv2.circle(image, (x1, y1), r, color, -1)
	cv2.circle(image, (x2, y2), r, color, -1)
	cv2.line(image, (x1, y1), (x2, y2), color)


def draw_cross(image, x1, x2, y1, y2, r, color=(0,0,255), thickness=3):
	cv2.line(image, (x1-r, y1-r), (x1+r, y1+r), color, thickness)
	cv2.line(image, (x1-r, y1+r), (x1+r, y1-r), color, thickness)
	cv2.line(image, (x2-r, y2-r), (x2+r, y2+r), color, thickness)
	cv2.line(image, (x2-r, y2+r), (x2+r, y2-r), color, thickness)


def draw_traces(img_control, img_query, kp_pairs, corners, status=None):
	h1, w1 = img_control.shape[:2]
	h2, w2 = img_query.shape[:2]
	img_combine = np.zeros((max(h1, h2), w1+w2), np.uint8)
	img_combine[:h1, :w1] = img_control
	img_combine[:h2, w1:w1+w2] = img_query
	img_combine = cv2.cvtColor(img_combine, cv2.COLOR_GRAY2BGR)

	offset_corners = np.int32(corners.reshape(-1, 2) + (w1, 0))
	draw_match_rect(img_combine, [offset_corners])

	if status is None:
		status = np.ones(len(kp_pairs), np.bool_)
	p1 = np.int32([kpp[0].pt for kpp in kp_pairs])
	p2 = np.int32([kpp[1].pt for kpp in kp_pairs]) + (w1, 0)

	# Draw inliers (if successfully found the object)
	# or matching keypoints (if failed)
	for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
		if inlier:
			draw_match_line(img_combine, x1, x2, y1, y2, 2)
		else:
			draw_cross(img_combine, x1, x2, y1, y2, 2)
	
	cv2.imshow("original", img_combine)


def get_corners(points):
	# Input: array of 4 coordinates [x,y]
	# Returns: [top-left,top-right,bottom-right,bottom-left]

	# rect = [top-left,top-right,bottom-right,bottom-left]
	rect = np.zeros((4, 2), dtype="float32")

	# Find top-left and bottom-right corners
	# Top-left has smallest sum
	# Bottom-right has largest sum
	s = points.sum(axis=1)
	rect[0] = points[np.argmin(s)]
	rect[2] = points[np.argmax(s)]

	# Find the top-right and bottom-left corners
	# Top-right: difference from x to y will be smallest
	# Bottom-left: difference from x to y will be smallest
	diff = np.diff(points, axis=1)
	rect[1] = points[np.argmin(diff)]
	rect[3] = points[np.argmax(diff)]

	return rect


def get_width_height(quad_corners):
	# Input: [top-left,top-right,bottom-right,bottom-left]
	# Output: (maximum_width,maximum_height)
	(tl, tr, br, bl) = quad_corners

	width_top = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	width_bottom = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))

	height_right = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	height_left = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

	max_width = max(int(width_top), int(width_bottom))
	max_height = max(int(height_left), int(height_right))

	return (max_width, max_height)

def filter_matches(kp1, kp2, matches, ratio=0.75):
	# matched key points
	mkp1, mkp2 = [], []
	for m in matches:
		if len(m) == 2 and m[0].distance < m[1].distance * ratio:
			m = m[0]
			mkp1.append( kp1[m.queryIdx] )
			mkp2.append( kp2[m.trainIdx] )
	p1 = np.float32([kp.pt for kp in mkp1])
	p2 = np.float32([kp.pt for kp in mkp2])
	kp_pairs = zip(mkp1, mkp2)
	return p1, p2, kp_pairs


def compute_perspective(img_control, img_query, corners):
	# Determine topleft,topright,bottomright,bottomleft corners
	query_rectangle = get_corners(corners.reshape(4,2))
	max_h, max_w = img_control.shape[:2]

	empty_array = np.array([
		[0, 0],
		[max_w-1, 0],
		[max_w-1, max_h-1],
		[0, max_h-1]], dtype="float32")

	# Calculates a perspective transform from four pairs of points
	perspective_transform_matrix = cv2.getPerspectiveTransform(query_rectangle, empty_array)

	# Transform query image based on matrix
	return cv2.warpPerspective(img_query, perspective_transform_matrix, (max_w, max_h))


def get_warped_image(img_control, img_query, draw_traces=False):
	img_control = resize(img_control)
	img_query = resize(img_query)

	detector = cv2.xfeatures2d.SIFT_create()
	matcher = cv2.BFMatcher(cv2.NORM_L2)

	# Find keypoints and descriptors
	keypoints1, descriptors1 = detector.detectAndCompute(img_control, None)
	keypoints2, descriptors2 = detector.detectAndCompute(img_query, None)

	# Find keypoints that match between the two images
	raw_matches = matcher.knnMatch(descriptors1, trainDescriptors=descriptors2, k=2)

	# Filter out weak matches
	points1, points2, kp_pairs = filter_matches(keypoints1, keypoints2, raw_matches)

	if len(points1) < 4:
		exit()
	
	# Find the transformation homography
	# H - 3x3 transformation matrix
	# status - vector of [0,1] one-hot values
	# Basic idea: img1 = H*img2
	H, status = cv2.findHomography(points1, points2, cv2.RANSAC, 5.0)
	#print "%d / %d  inliers/matched" % (np.sum(status), len(status))

	if H is None:
		exit()

	# Extract corners in the query image
	h1, w1 = img_control.shape[:2]
	h2, w2 = img_query.shape[:2]
	blank_array = np.float32([[0,0], [w1,0], [w1,h1], [0,h1]]).reshape(2,-1,2)
	corners = cv2.perspectiveTransform(blank_array, H)

	if draw_traces:
		# Draw matching keypoint pairs for debugging
		# Traces can only be drawn on grayscale images
		gray_control = cv2.cvtColor(img_control, cv2.COLOR_BGR2GRAY)
		gray_query = cv2.cvtColor(img_query, cv2.COLOR_BGR2GRAY)
		draw_traces(gray_control, gray_query, kp_pairs, corners, status)

	warped = compute_perspective(img_control, img_query, corners)
	return warped


def resize(img, maximum_small_edge=500):
	h = img.shape[0]
	w = img.shape[1]
	small_edge = h if h < w else w

	# If the image is already 500px or smaller on the shorter edge
	if small_edge <= maximum_small_edge:
		return img

	scale_ratio = 1 / (small_edge*1.0 / maximum_small_edge)
	return cv2.resize(img, (0,0), fx=scale_ratio, fy=scale_ratio)


