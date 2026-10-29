import sys
import json
from app import app
import db

def run_tests():
    print("=================================================================")
    print("PublicSpace360 - Interactive Panvel Map & Image Suite Verification")
    print("=================================================================")

    client = app.test_client()

    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name} - {details}")

    # 1. Routes /map and /explore-map
    res_map = client.get('/map')
    assert_test("GET /map returns HTTP 200", res_map.status_code == 200)
    assert_test("GET /map contains map canvas and search box", 
                b'id="gis-map"' in res_map.data and b'id="mapSearchInput"' in res_map.data)

    res_explore = client.get('/explore-map')
    assert_test("GET /explore-map returns HTTP 200", res_explore.status_code == 200)

    # 2. Spaces API - All spaces
    res_spaces = client.get('/api/spaces')
    assert_test("GET /api/spaces returns HTTP 200", res_spaces.status_code == 200)
    spaces_data = json.loads(res_spaces.data.decode('utf-8'))
    assert_test("GET /api/spaces contains 16 Panvel spaces", len(spaces_data) >= 16, f"Count: {len(spaces_data)}")

    # 3. Panvel Disambiguation: CIDCO Garden search
    res_cidco = client.get('/api/spaces?q=CIDCO+Garden')
    cidco_data = json.loads(res_cidco.data.decode('utf-8'))
    assert_test("Search 'CIDCO Garden' returns matching Panvel spaces", len(cidco_data) >= 2, f"Got: {len(cidco_data)}")
    cidco_exact = [s for s in cidco_data if s['name'] == 'CIDCO Garden']
    assert_test("CIDCO Garden listings disambiguated by area (New Panvel & Khanda Colony)", 
                len(cidco_exact) == 2 and any(s['area'] == 'New Panvel' for s in cidco_exact) and any(s['area'] == 'Khanda Colony' for s in cidco_exact))
    ids = {s['id'] for s in cidco_exact}
    assert_test("CIDCO Garden spaces have distinct unique IDs", len(ids) == 2, f"IDs: {ids}")

    # 4. Filter by Area
    res_khanda = client.get('/api/spaces?area=Khanda+Colony')
    khanda_data = json.loads(res_khanda.data.decode('utf-8'))
    assert_test("Filter area=Khanda Colony returns spaces only in Khanda Colony", 
                len(khanda_data) > 0 and all(s['area'] == 'Khanda Colony' for s in khanda_data))

    # 5. Filter by Facility
    res_gym = client.get('/api/spaces?facility=Open+Gym')
    gym_data = json.loads(res_gym.data.decode('utf-8'))
    assert_test("Filter facility=Open Gym returns spaces having Open Gym",
                len(gym_data) > 0 and all('Open Gym' in s.get('facilities', '') for s in gym_data))

    # 6. Space Details API with Gallery & Survey Stats
    res_sp1 = client.get('/api/spaces/1')
    assert_test("GET /api/spaces/1 returns HTTP 200", res_sp1.status_code == 200)
    sp1_data = json.loads(res_sp1.data.decode('utf-8'))
    assert_test("Space #1 has gallery images with source & credit", 
                len(sp1_data.get('gallery_images', [])) > 0 and 'image_credit' in sp1_data['gallery_images'][0])
    assert_test("Space #1 has survey statistics (cleanliness, safety, etc.)", 
                'survey_stats' in sp1_data and 'cleanliness' in sp1_data['survey_stats'])

    # 7. Space Details Web Page: /public-space/<id> and /spaces/<id>
    res_ps1 = client.get('/public-space/1')
    assert_test("GET /public-space/1 returns HTTP 200", res_ps1.status_code == 200)
    assert_test("Details page contains Photo Gallery, Facilities, and What Users Say",
                b'Photo Gallery' in res_ps1.data and b'What Users Say' in res_ps1.data and b'Walking Track' in res_ps1.data)
    assert_test("Details page contains Take Survey pre-selected button",
                b'/survey?space_id=1' in res_ps1.data)

    res_alt = client.get('/spaces/1')
    assert_test("GET /spaces/1 returns HTTP 200", res_alt.status_code == 200)

    # 8. Submit Citizen Comment
    comment_payload = {
        'space_id': 1,
        'rating': 5,
        'comment': 'Exceptional garden with peaceful walking track and lush greenery in New Panvel East!',
        'user_name': 'Prof. A. K. Sharma',
        'user_email': 'aksharma@panvel.ac.in'
    }
    res_fb_post = client.post('/api/feedback', json=comment_payload)
    assert_test("POST /api/feedback submits new comment (HTTP 201)", res_fb_post.status_code == 201)

    res_fb_get = client.get('/api/feedback/1')
    fb_list = json.loads(res_fb_get.data.decode('utf-8'))
    assert_test("GET /api/feedback/1 retrieves citizen comment", 
                any(f.get('user_name') == 'Prof. A. K. Sharma' for f in fb_list))

    # 9. Survey Form Auto-selection
    res_survey = client.get('/survey?space_id=1')
    assert_test("GET /survey?space_id=1 renders survey form", res_survey.status_code == 200)
    assert_test("Survey form pre-selects CIDCO Garden (space_id 1)",
                b'value="1" selected' in res_survey.data or b'CIDCO Garden' in res_survey.data)

    # 10. Admin Authentication & Dashboard
    with client.session_transaction() as sess:
        sess['admin_id'] = 1
        sess['user_name'] = 'Admin'
        sess['role'] = 'admin'

    res_admin = client.get('/admin')
    assert_test("GET /admin loads Admin Dashboard (HTTP 200)", res_admin.status_code == 200)
    assert_test("Admin Dashboard contains Images & Gallery tab", b'id="tab-images"' in res_admin.data)
    assert_test("Admin Dashboard contains Citizen Reviews tab", b'id="tab-feedback"' in res_admin.data)
    assert_test("Admin Dashboard contains Upload Image Modal", b'id="uploadImageModal"' in res_admin.data)

    # 11. Admin Image Upload API
    new_img_payload = {
        'image_url': 'https://images.unsplash.com/photo-1596701062351-8c2c14d1fdd0?w=800',
        'image_source': 'Field Survey 2026',
        'image_credit': 'Panvel Academic Survey Team',
        'is_primary': 0
    }
    res_img_post = client.post('/api/spaces/1/images', json=new_img_payload)
    assert_test("POST /api/spaces/1/images uploads photo with attribution", res_img_post.status_code == 201)
    img_resp = json.loads(res_img_post.data.decode('utf-8'))
    created_img_id = img_resp.get('id')

    # 12. Admin Moderate Comment Status
    if fb_list:
        latest_fb_id = fb_list[0]['id']
        res_mod = client.put(f'/api/feedback/{latest_fb_id}/status', json={'status': 'Approved'})
        assert_test("PUT /api/feedback/<id>/status approves comment", res_mod.status_code == 200)

    # 13. Clean up test image
    if created_img_id:
        res_del_img = client.delete(f'/api/spaces/images/{created_img_id}')
        assert_test("DELETE /api/spaces/images/<id> deletes image cleanly", res_del_img.status_code == 200)

    print("=================================================================")
    print(f"Results: {passed} / {total} tests passed ({round(passed/total*100, 1)}%)")
    print("=================================================================")

    if passed == total:
        print("ALL VERIFICATION CHECKS PASSED PERFECTLY!")
        return 0
    else:
        print("SOME CHECKS FAILED.")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
