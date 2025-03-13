from onvif import ONVIFCamera


def get_retsp_onvif(camera_ip, camera_port, username, password):
    try:
        camera = ONVIFCamera(camera_ip, port=camera_port, user=username, passwd=password)
        media_service = camera.create_media_service()
        profiles = media_service.GetProfiles()
        print(f"Profiles: {media_service}")
        profile_token = profiles[0].token

        stream_setup = {
            'Stream': 'RTP-Unicast',
            'Transport': {'Protocol': 'RTSP'}
        }

        stream_uri = media_service.GetStreamUri({'StreamSetup': stream_setup, 'ProfileToken': profile_token})

        print("RTSP URL:", stream_uri.Uri)
        return stream_uri.Uri

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        return None


# print(get_retsp_onvif("192.168.103.240",80,"root","Oryza@123"))

def snapshot_onvif(camera_ip, camera_port, username, password):
    try:
        camera = ONVIFCamera(camera_ip, camera_port, username, password)
        # Lấy dịch vụ media
        media_service = camera.create_media_service()

        # Lấy cấu hình video profiles có sẵn
        profiles = media_service.GetProfiles()

        # Chọn profile đầu tiên
        profile_token = profiles[0].token
        print(f"Profile Token: {profile_token}")

        # Lấy thông tin luồng hình ảnh tĩnh (Snapshot)
        snapshot_uri = media_service.GetSnapshotUri({'ProfileToken': profile_token})

        # Kiểm tra URI
        print(f"Snapshot URI: {snapshot_uri.Uri}")

        # Tải về hình ảnh từ URI
        # response = requests.get(snapshot_uri.Uri,
        #                         auth=HTTPDigestAuth(username, password))
        #
        # # Kiểm tra nội dung trả về
        # print(f"Response Content-Type: {response.headers['Content-Type']}")
        #
        # # Kiểm tra nếu đó là hình ảnh
        # if 'image' in response.headers['Content-Type']:
        #     image = Image.open(BytesIO(response.content))
        #     image.show()  # Hiển thị hình ảnh
        #     # image.save('snapshot.jpg')  # Lưu hình ảnh nếu cần
        # else:
        #     print("Error: Response is not an image.")
        #     print(response.content)  # Debug the response content if it's not an image


    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        return None

# snapshot_onvif("192.168.104.200", 2011, "admin", "Oryza@123")
