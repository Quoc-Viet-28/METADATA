from io import BytesIO
from typing import Optional
import base64
from beanie import PydanticObjectId
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Form
from fastapi.responses import StreamingResponse
from app.core.security import get_user_info
from app.dto.person_dto import PersonCreate, PersonUpdate, PersonResponse
from app.services.person_service import person_service
from app.utils.image_handle import ImageHandle
from app.utils.minio_utils import MinioServices
from app.utils.common_utils import get_company

router = APIRouter()
prefix = "/person"
tags = ["person"]

image_handle = ImageHandle()


@router.post("/create")
async def create(request: PersonCreate, user=Depends(get_user_info())):
    return await person_service.create(request, user)




@router.post("/validate-image")
def validate_image(file: UploadFile = File(...)):
    file = file.file.read()
    image = image_handle.convert_image(file)
    list_image = image_handle.check_face(image)
    if len(list_image) == 0:
        print("Không tìm thấy khuôn mặt")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khuôn mặt"
        )

    list_bas64 = []
    for img in list_image:
        byte = image_handle.convert_image_to_byte(img)
        # save image to jpg
        # with open("dfgsadfgsdfg.jpg", "wb") as f:
        #     f.write(byte)
        #
        # # convert byte to base64
        img_b = base64.b64encode(byte).decode("utf-8")
        list_bas64.append(img_b)

    return list_bas64


@router.put("/update/{id_person}")
async def update(id_person: PydanticObjectId, request: PersonUpdate, user=Depends(get_user_info())):
    return await person_service.update(request, id_person, user)


@router.get("/get-all", response_model=list[PersonResponse])
async def get_all(id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info()),
                  keyword: Optional[str] = None, type_person: Optional[str] = None, page: int = 0, size: int = 10):
    return await person_service.get_all(id_company, keyword, type_person, page, size, user)


@router.get("/get-count")
async def get_count(id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info()),
                    keyword: Optional[str] = None, type_person: Optional[str] = None):
    return await person_service.get_count(id_company, keyword, type_person, user)

@router.post("/add-user-from-file")
async def add_user_from_file(
    file: UploadFile = File(...),
    mapping_data: str = Form(None),
    user=Depends(get_user_info())
    ):
        minio_service = MinioServices()
        image_cache = {}
        rows = []
        row_data = {}
        errors_exist = False
        image_column = None
        contents = file.file.read()
        excel_data, header_data_excel, header_person_create, unmatched_headers, image_loader, sheet, data_mapping, full_mapping = await person_service.process_excel_and_generate_mapping(contents, mapping_data)
        if unmatched_headers and mapping_data is None:
            return header_data_excel
        id_company = PydanticObjectId('67316a451f404281e8362e8a')
        # company = await get_company(user,None)
        company = await get_company(user, id_company)
        for idx, mapped_row in enumerate(data_mapping):
            try:
                row_data["image"] = None
                row_data = mapped_row.copy()
                if "image" in full_mapping:
                    image_header = full_mapping["image"]
                    if image_header in header_data_excel:
                        image_column = header_data_excel.index(image_header)
                        if image_column is not None:
                            cell_row = idx + 2
                            cell_column = sheet.cell(row=1, column=image_column + 1).column_letter
                            image_key = f"{cell_column}{cell_row}"
                            if image_loader.image_in(image_key):
                                image_bytes = BytesIO()
                                image_save = image_loader.get(image_key)
                                image_save.save(image_bytes, format=image_save.format)
                                image_bytes.seek(0)
                                image_cache[idx] = image_bytes
                                validated_images = validate_image(file=UploadFile(file=image_bytes))
                                for img_base64 in validated_images:
                                    img_bytes_test = base64.b64decode(img_base64)
                                    img_io = BytesIO(img_bytes_test)
                                    url = await minio_service.upload_file_from_bytesIO(img_io,f'image_{idx}.{image_save.format}')
                                    row_data["image"] = url
                row_data["id_company"] = company.id
                person_create = await person_service.create_person_instance(row_data)
                rows.append(person_create)
            except Exception as e:
                excel_data.at[idx, "errors"] = str(e)
                errors_exist = True
                print("ERROR: ", e)

        if errors_exist:
            output = await person_service.handle_errors(excel_data, image_cache, image_column, sheet)
            return StreamingResponse(
                output,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename="processed_file.xlsx"'}
            )
        else:
            for person_create in rows:
                await create(person_create, user)
            return {"message": "Thêm người dùng thành công."}


@router.get("/download-template-add-user")
async def download_template_add_user():
    return await person_service.download_template_add_user()
